# -*- coding: utf-8 -*-

"""Pibooth diagnostic module.
"""

import argparse
import io
import os
import platform
import subprocess
import sys
import time

import pygame
from PIL import Image
try:
    import gphoto2 as gp
except Exception:
    gp = None  # gphoto2 is optional (or its shared libraries are missing)
import pibooth
from pibooth import language
from pibooth.config import PiboothConfigParser
from pibooth.counters import Counters
from pibooth.printer import Printer
from pibooth.utils import configure_logging
from pibooth.plugins import create_plugin_manager
from pibooth.view import get_window


LOGFILE = None
APPNAME = 'diagnostic'


def gp_logging(level, domain, string, data=None):
    write_log(f'Gphoto2: {domain}: {string}')


def open_log(name):
    """Start a new log file, return its name.
    """
    global LOGFILE
    if LOGFILE:
        LOGFILE.close()
    LOGFILE = open(name + '.log', 'w')
    return name + '.log'


def write_log(text, new_section=False):
    """Write text in the log file"""
    global LOGFILE
    if not LOGFILE:
        LOGFILE = open(APPNAME + '.log', 'w')

    if new_section:
        print('\n' + '=' * 80)
        LOGFILE.write('\n' + '=' * 80 + '\n')

    text = str(text)
    print(text[:200])
    if len(text) > 200:
        print("[... -> see log file for full message]")
    LOGFILE.write(text + '\n')


def _shell(command):
    """Return the output of the given command, None if it can not be run.
    """
    try:
        return subprocess.check_output(command, shell=True, stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return None


def _cpu_model():
    """Return the CPU/board model.
    """
    for filename, prefix in (('/proc/device-tree/model', None), ('/proc/cpuinfo', 'Model')):
        try:
            with open(filename, 'r') as fp:
                content = fp.read()
        except IOError:
            continue
        if prefix is None:
            return content.strip('\x00').strip()
        for line in content.splitlines():
            if line.startswith(prefix):
                return line.split(':', 1)[1].strip()
    return platform.processor() or platform.machine()


def log_environment(window):
    """Print everything which has an influence on the display performances.
    """
    surface = window.surface
    write_log("Board / CPU     : {}".format(_cpu_model()))
    write_log("OS              : {} ({})".format(platform.platform(), platform.machine()))
    write_log("Python          : {}".format(platform.python_version()))
    write_log("Pibooth         : {}".format(pibooth.__version__))
    write_log("Pygame / SDL    : {} / {}".format(
        pygame.version.ver, '.'.join(str(v) for v in pygame.version.SDL)))
    write_log("SDL driver      : {} (SDL_VIDEODRIVER={})".format(
        pygame.display.get_driver(), os.environ.get('SDL_VIDEODRIVER', 'unset')))
    write_log("Window          : {}x{}, {} bits/px, flags=0x{:08x}".format(
        surface.get_width(), surface.get_height(), surface.get_bitsize(),
        surface.get_flags() & 0xFFFFFFFF))
    write_log("  HWSURFACE={} DOUBLEBUF={} FULLSCREEN={}".format(
        bool(surface.get_flags() & pygame.HWSURFACE),
        bool(surface.get_flags() & pygame.DOUBLEBUF),
        bool(surface.get_flags() & pygame.FULLSCREEN)))

    for label, command in (("Temperature     ", "vcgencmd measure_temp"),
                           ("ARM frequency   ", "vcgencmd measure_clock arm")):
        out = _shell(command)
        if out:
            write_log("{}: {}".format(label, out))
    log_throttling()
    write_log("")


THROTTLING_FLAGS = ((0, "under-voltage RIGHT NOW"),
                    (1, "ARM frequency capped RIGHT NOW"),
                    (2, "throttled RIGHT NOW"),
                    (3, "soft temperature limit reached RIGHT NOW"),
                    (16, "under-voltage has occurred since boot"),
                    (17, "ARM frequency capping has occurred since boot"),
                    (18, "throttling has occurred since boot"),
                    (19, "soft temperature limit has occurred since boot"))


def log_throttling():
    """Decode `vcgencmd get_throttled`.
    """
    out = _shell("vcgencmd get_throttled")
    if not out or '=' not in out:
        return
    try:
        value = int(out.split('=')[1], 0)
    except ValueError:
        return
    write_log("Throttling      : {}".format(out))
    for bit, reason in THROTTLING_FLAGS:
        if value & (1 << bit):
            write_log("    - {}".format(reason))
    if value & 0b1111:
        write_log("    /!\\ The board is slowed down right now, check the power supply")


def measure(label, func, duration=1.0, unit='ms'):
    """Call `func` during `duration` seconds, log and return the mean call time.
    """
    func()  # Warm-up
    count, elapsed = 0, 0.0
    start = time.perf_counter()
    while time.perf_counter() - start < duration:
        tick = time.perf_counter()
        func()
        elapsed += time.perf_counter() - tick
        count += 1
    mean = elapsed / count * 1000
    write_log("  {:<46} {:8.2f} {}  ({} calls)".format(label, mean, unit, count))
    return mean


def diagnose_display_refresh(window, menu_rect):
    """Cost of pushing the window to the display at each frame.
    """
    surface = window.surface
    write_log("Display refresh (what the main loop pays at each frame)")
    full = measure("pygame.display.update() -> full screen",
                   lambda: pygame.display.update())
    partial = measure("pygame.display.update(menu_rect) -> {}x{}".format(menu_rect.width, menu_rect.height),
                      lambda: pygame.display.update(menu_rect))
    measure("surface.fill() -> full screen (memory speed)",
            lambda: surface.fill((0, 0, 0)))
    write_log("")
    if full > 0.01 and partial / full > 0.7:
        write_log("  /!\\ Refreshing a small area costs as much as the full screen: SDL")
        write_log("      pushes the whole window whatever the given rectangles.")
    write_log("")
    return full, partial


def _describe(surface):
    """Return the pixel format of a surface as a readable string.
    """
    red, green, blue, alpha = surface.get_masks()
    return "{} bits, R={:08x} G={:08x} B={:08x} A={:08x}".format(
        surface.get_bitsize(), red, green, blue, alpha)


def diagnose_blits(window, menu_rect):
    """Cost of the blits painting the menu is made of.
    """
    write_log("Pixel formats")
    default = pygame.Surface(menu_rect.size, pygame.SRCALPHA, 32)
    write_log("  {:<28} {}".format("window surface", _describe(window.surface)))
    write_log("  {:<28} {}".format("pygame_menu surfaces", _describe(default)))
    converted = default.convert_alpha()
    write_log("  {:<28} {}".format("after convert_alpha()", _describe(converted)))
    write_log("  {:<28} {}".format(
        "formats match", "yes" if default.get_masks() == converted.get_masks() else "NO"))
    write_log("")

    write_log("Blit of a {}x{} area (what painting the menu is made of)".format(
        menu_rect.width, menu_rect.height))
    opaque = pygame.Surface(menu_rect.size)
    opaque.fill((80, 80, 80))
    for surface in (default, converted):
        surface.fill((80, 80, 80, 128))

    plain = measure("opaque, no blending (reference)",
                    lambda: window.surface.blit(opaque, menu_rect))
    blended = measure("transparent, format of pygame_menu",
                      lambda: window.surface.blit(default, menu_rect))
    fixed = measure("transparent, converted to the window format",
                    lambda: window.surface.blit(converted, menu_rect))
    measure("transparent, blended by SDL instead of pygame",
            lambda: window.surface.blit(default, menu_rect,
                                        special_flags=pygame.BLEND_ALPHA_SDL2))
    write_log("")
    write_log("  Blending costs {:.0f} times a plain copy, {:.0f} times once converted.".format(
        blended / plain, fixed / plain))
    write_log("")


def diagnose_menu(window):  # pylint: disable=protected-access
    """Cost of the menu itself, without any display refresh.
    """
    menu = window._menu
    write_log("Settings menu (without any display refresh)")
    events = [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN, unicode='',
                                 mod=0, scancode=0, test=True)]
    measure("menu.update() -> handle the events", lambda: menu._main_menu.update([]))
    measure("menu.update() -> handle a key press", lambda: menu._main_menu.update(list(events)))
    slow = measure("menu.draw() -> blended by pygame",
                   lambda: menu._main_menu.draw(window.surface))
    fast = measure("menu.draw() -> blended by SDL (what pibooth does)",
                   lambda: menu.draw(window.surface))
    write_log("")
    if fast < slow:
        write_log(f"  Handing the blending over to SDL makes painting the menu {slow / fast:.1f} times")
        write_log(f"  faster, {slow - fast:.0f} ms saved on each frame.")
    else:
        write_log("  Handing the blending over to SDL changes nothing on this machine.")
    write_log("")


def diagnose_loop(window, duration=3.0):
    """Reproduce the main loop to get the frame rate really achieved.
    """
    write_log(f"Main loop reproduced during {duration:.0f} seconds (a key press is handled once per frame)")
    clock = pygame.time.Clock()
    works, periods = [], []
    start = time.perf_counter()
    while time.perf_counter() - start < duration:
        tick = time.perf_counter()
        events = list(pygame.event.get())
        events.append(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN, unicode='',
                                         mod=0, scancode=0, test=True))
        window.update(events)
        pygame.display.update(window.draw())
        works.append((time.perf_counter() - tick) * 1000)
        clock.tick(25)  # Same frame rate limit as the application
        periods.append((time.perf_counter() - tick) * 1000)

    works.sort()
    periods.sort()
    work = sum(works) / len(works)
    period = sum(periods) / len(periods)
    write_log("  {:<46} {:8.2f} ms".format("work done in a frame (mean)", work))
    write_log("  {:<46} {:8.2f} ms".format("work done in a frame (slowest 5%)", works[int(len(works) * 0.95)]))
    write_log("  {:<46} {:8.2f} ms".format("frame period, waiting included (mean)", period))
    write_log("  {:<46} {:8.1f} fps".format("frame rate achieved (25 fps requested)", 1000 / period))
    write_log("")
    write_log("  A key press is seen at the next frame and painted at the one after,")
    write_log(f"  its latency is thus roughly {2 * period:.0f} ms.")
    if work > 1000 / 25 - 18:
        write_log("  The loop is limited by the work itself, not by the frame rate limit.")
    else:
        write_log("  The loop is limited by the frame rate limit, not by the work itself.")
    write_log("")


def print_config(config, parent=''):
    """Print all parameters of the camera"""

    gp_widget_types = {gp.GP_WIDGET_WINDOW: "Window toplevel",
                       gp.GP_WIDGET_SECTION: "Section (or Tab)",
                       gp.GP_WIDGET_TEXT: "Text",
                       gp.GP_WIDGET_RANGE: "Slider",
                       gp.GP_WIDGET_TOGGLE: "Toggle button (or check box)",
                       gp.GP_WIDGET_RADIO: "Radio button",
                       gp.GP_WIDGET_MENU: "Menu widget (same as Radio)",
                       gp.GP_WIDGET_BUTTON: "Button press",
                       gp.GP_WIDGET_DATE: "Date entering",
                       }

    for child in config.get_children():
        path = '/'.join((parent, child.get_name()))
        if child.get_type() == gp.GP_WIDGET_SECTION:
            print_config(child, path)
        else:
            write_log(f'{path}')
            write_log(f'  Label       : {child.get_label()}')
            write_log(f'  Readonly    : {"yes" if child.get_readonly() else "no"}')
            write_log(f'  Data type   : {type(child.get_value())}')
            write_log(f'  Widget type : {gp_widget_types[child.get_type()]}')
            write_log(f'  Current     : {child.get_value()}')
            if child.get_type() == gp.GP_WIDGET_RADIO:
                write_log(f'  Choices     : {[c for c in child.get_choices()]}')
            elif child.get_type() == gp.GP_WIDGET_RANGE:
                write_log('  Choices     : min={}, max={}, step={}'.format(*child.get_range()))
            elif child.get_type() == gp.GP_WIDGET_TOGGLE:
                write_log('  Choices     : [0, 1]')
            elif child.get_type() == gp.GP_WIDGET_MENU:
                write_log(f'  Choices     : {[child.get_choice(n) for n in range(child.count_choices())]}')
            else:
                write_log('  Choices     : n/a')


def set_config_value(camera, section, option, value):
    """Set camera configuration. """
    try:
        write_log(f'Setting option {section}/{option}="{value}"')
        config = camera.get_config()
        child = config.get_child_by_name(section).get_child_by_name(option)
        if child.get_type() == gp.GP_WIDGET_RADIO:
            choices = [c for c in child.get_choices()]
        else:
            choices = None

        if choices and value not in choices:
            write_log(f"   -> invalid value '{value}' for option {option} (possible choices: {choices})")
        child.set_value(value)
        camera.set_config(config)
    except gp.GPhoto2Error:
        write_log(f"   -> unsupported setting {section}/{option}={value} (nothing configured on DSLR)")


def get_config_value(camera, section, option):
    """Get camera configuration option.
    """
    try:
        config = camera.get_config()
        child = config.get_child_by_name(section).get_child_by_name(option)
        value = child.get_value()
        write_log(f'Getting option {section}/{option}={value}')
        return value
    except gp.GPhoto2Error:
        write_log(f'Unknown option {section}/{option}')


def camera_connected():
    """Return the list of connected camera compatible with gPhoto2.
    """
    if hasattr(gp, 'gp_camera_autodetect'):
        # gPhoto2 version 2.5+
        cameras = gp.check_result(gp.gp_camera_autodetect())
    else:
        port_info_list = gp.PortInfoList()
        port_info_list.load()
        abilities_list = gp.CameraAbilitiesList()
        abilities_list.load()
        cameras = abilities_list.detect(port_info_list)
    return cameras


def diagnose_display(config, plugin_manager):
    """Measure what the settings menu costs to open and to paint.
    """
    write_log("Starting diagnostic of the display", True)
    try:
        size = config.gettyped('WINDOW', 'size')
        window = get_window('pygame', "Pibooth diagnostic",
                            (800, 480) if isinstance(size, str) else size,
                            config.gettyped('WINDOW', 'background'),
                            config.gettyped('WINDOW', 'text_color'))
        if isinstance(size, str) and size.lower() == 'fullscreen':
            window.toggle_fullscreen()
        window.surface.fill((17, 90, 140))
        pygame.display.update()
    except Exception as ex:
        write_log(f"No usable display, skipping: {ex}")
        driver = pygame.display.get_driver() if pygame.display.get_init() else 'none'
        write_log(f"  SDL driver '{driver}', DISPLAY={os.environ.get('DISPLAY', 'unset')}")
        write_log("  Run this from the screen of the booth, or set DISPLAY (usually :0)")
        return

    try:
        language.init(config.join_path("translations.cfg"))
        plugin_manager.hook.pibooth_configure(cfg=config)

        log_environment(window)

        class _App:  # pylint: disable=too-few-public-methods
            count = Counters(config.join_path("counters.json"), taken=0, printed=0,
                             forgotten=0, remaining_duplicates=0)
            # The menu is built differently when a printer is installed
            printer = Printer(config.get('PRINTER', 'printer_name'),
                              config.getint('PRINTER', 'max_pages'),
                              config.gettyped('PRINTER', 'printer_options'))

        window.set_menu(_App(), config, plugin_manager)
        tick = time.perf_counter()
        window.toggle_menu()
        window.update([])
        window.draw()
        built = (time.perf_counter() - tick) * 1000
        write_log(f"Settings menu built in {built:.0f} ms (paid each time the menu is opened)")
        write_log("")

        menu_rect = window._menu.get_rect(window.surface)  # pylint: disable=protected-access
        diagnose_display_refresh(window, menu_rect)
        diagnose_blits(window, menu_rect)
        diagnose_menu(window)
        diagnose_loop(window)
    except Exception as ex:
        write_log(f"ABORT   : exception occures: {ex}")
    finally:
        pygame.quit()


def log_context(plugin_manager):
    """Write what is common to every diagnostic.
    """
    write_log(f"Pibooth version installed: {pibooth.__version__}")
    plugins = ", ".join([plugin_manager.get_friendly_name(p) for p in plugin_manager.list_external_plugins()])
    write_log(f"Installed plugins: {plugins}")


def diagnose_dslr():
    """Check that a connected DSLR answers the commands used by pibooth.
    """
    error = False
    if not gp:
        write_log("gPhoto2 not installed, cannot diagnose connected DSLR")
        sys.exit(1)

    try:
        info = gp.version.gp_library_version(gp.version.GP_VERSION_VERBOSE)
        write_log(f"GPhoto2 version installed: {info[0]}")
        for opt in info[1:]:
            write_log(f"  - {opt}")
    except Exception:
        pass

    gp_log_callback = gp.check_result(gp.gp_log_add_func(gp.GP_LOG_VERBOSE, gp_logging))
    write_log("Listing all connected DSLR camera")
    cameras_list = camera_connected()

    if not cameras_list:
        write_log('No compatible DSLR camera detected')
        sys.exit(1)

    cameras_list = sorted(cameras_list, key=lambda x: x[0])
    for index, (name, addr) in enumerate(cameras_list):
        write_log(f"{index:02d} : addr-> {addr}  name-> {name}")

    write_log("Starting diagnostic of connected DSLR camera", True)
    camera = gp.Camera()
    camera.init()

    abilities = camera.get_abilities()
    preview_compat = gp.GP_OPERATION_CAPTURE_PREVIEW == abilities.operations & gp.GP_OPERATION_CAPTURE_PREVIEW
    write_log(f"* Preview compatible: {preview_compat}")
    capture_compat = gp.GP_OPERATION_CAPTURE_IMAGE == abilities.operations & gp.GP_OPERATION_CAPTURE_IMAGE
    write_log(f"* Capture compatible: {capture_compat}")

    if capture_compat:
        try:
            print_config(camera.get_config())

            write_log("Testing commands used by pibooth", True)

            set_config_value(camera, 'imgsettings', 'iso', '100')
            set_config_value(camera, 'settings', 'capturetarget', 'Memory card')

            viewfinder = get_config_value(camera, 'actions', 'viewfinder')
            if viewfinder is not None:
                set_config_value(camera, 'actions', 'viewfinder', 1)

            write_log("Take capture preview")
            camera.capture_preview()

            if viewfinder is not None:
                set_config_value(camera, 'actions', 'viewfinder', 0)

            write_log("Take a capture")
            gp_path = camera.capture(gp.GP_CAPTURE_IMAGE)

            write_log("Download file from DSLR")
            camera_file = camera.file_get(gp_path.folder, gp_path.name, gp.GP_FILE_TYPE_NORMAL)

            write_log("Save capture locally from memory buffer")
            data = camera_file.get_data_and_size()
            with open(APPNAME + '.raw', 'wb') as fd:
                fd.write(data)
            image = Image.open(io.BytesIO(data))
            image.save(APPNAME + '.jpg')

        except Exception as ex:
            write_log(f"ABORT   : exception occures: {ex}", True)
            error = True

    del gp_log_callback
    camera.exit()
    return not error


def main():
    """Application entry point.
    """
    parser = argparse.ArgumentParser(usage="%(prog)s [options]", description=__doc__)
    parser.add_argument("--dslr", action='store_true',
                        help="diagnose the connected DSLR camera (default)")
    parser.add_argument("--display", action='store_true',
                        help="diagnose the performances of the display and of the settings menu")
    options = parser.parse_args()
    if not options.dslr and not options.display:
        options.dslr = True  # Historical behavior of the command

    configure_logging()
    plugin_manager = create_plugin_manager()
    config = PiboothConfigParser("~/.config/pibooth/pibooth.cfg", plugin_manager)
    plugin_manager.load_all_plugins(config.gettuple('GENERAL', 'plugins', 'path'),
                                    config.gettuple('GENERAL', 'plugins_disabled', str))

    if options.display:
        # Its own file: the measurements change at each run, they would make the
        # DSLR report unstable and it is meant to be compared and contributed
        filename = open_log(APPNAME + '-display')
        log_context(plugin_manager)
        diagnose_display(config, plugin_manager)
        write_log("SUCCESS : diagnostic completed", True)
        write_log("If you are investigating why pibooth is slow, please paste the")
        write_log(f"content of generated file '{filename}'")
        write_log("on https://github.com/pibooth/pibooth/issues")

    if options.dslr:
        filename = open_log(APPNAME)
        log_context(plugin_manager)
        if diagnose_dslr():
            write_log("SUCCESS : diagnostic completed", True)
        write_log("If you are investigating why pibooth does not work with your DSLR camera,")
        write_log(f"please paste the content of generated file '{filename}'")
        write_log("on https://github.com/pibooth/pibooth/issues")
