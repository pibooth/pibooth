# -*- coding: utf-8 -*-

"""Pibooth diagnostic module.
"""

import io
import sys
from PIL import Image
try:
    import gphoto2 as gp
except ImportError:
    gp = None  # gphoto2 is optional
import pibooth
from pibooth.config import PiConfigParser
from pibooth.utils import configure_logging
from pibooth.plugins import create_plugin_manager


LOGFILE = None
APPNAME = 'diagnostic'


def gp_logging(level, domain, string, data=None):
    write_log('Gphoto2: {}: {}'.format(domain, string))


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
            write_log('{}'.format(path))
            write_log('  Label       : {}'.format(child.get_label()))
            write_log('  Readonly    : {}'.format('yes' if child.get_readonly() else 'no'))
            write_log('  Data type   : {}'.format(type(child.get_value())))
            write_log('  Widget type : {}'.format(gp_widget_types[child.get_type()]))
            write_log('  Current     : {}'.format(child.get_value()))
            if child.get_type() == gp.GP_WIDGET_RADIO:
                write_log('  Choices     : {}'.format([c for c in child.get_choices()]))
            elif child.get_type() == gp.GP_WIDGET_RANGE:
                write_log('  Choices     : min={}, max={}, step={}'.format(*child.get_range()))
            elif child.get_type() == gp.GP_WIDGET_TOGGLE:
                write_log('  Choices     : [0, 1]')
            elif child.get_type() == gp.GP_WIDGET_MENU:
                write_log('  Choices     : {}'.format([child.get_choice(n) for n in range(child.count_choices())]))
            else:
                write_log('  Choices     : n/a')


def set_config_value(camera, section, option, value):
    """Set camera configuration. """
    try:
        write_log('Setting option {}/{}="{}"'.format(section, option, value))
        config = camera.get_config()
        child = config.get_child_by_name(section).get_child_by_name(option)
        if child.get_type() == gp.GP_WIDGET_RADIO:
            choices = [c for c in child.get_choices()]
        else:
            choices = None

        if choices and value not in choices:
            write_log("   -> invalid value '{}' for option {} (possible choices: {})".format(value, option, choices))
        child.set_value(value)
        camera.set_config(config)
    except gp.GPhoto2Error:
        write_log('   -> unsupported setting {}/{}={} (nothing configured on DSLR)'.format(section, option, value))


def get_config_value(camera, section, option):
    """Get camera configuration option.
    """
    try:
        config = camera.get_config()
        child = config.get_child_by_name(section).get_child_by_name(option)
        value = child.get_value()
        write_log('Getting option {}/{}={}'.format(section, option, value))
        return value
    except gp.GPhoto2Error:
        write_log('Unknown option {}/{}'.format(section, option))


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


def main():
    error = False
    configure_logging()
    write_log("Pibooth version installed: {}".format(pibooth.__version__))

    plugin_manager = create_plugin_manager()
    config = PiConfigParser("~/.config/pibooth/pibooth.cfg", plugin_manager)

    # Register plugins
    plugin_manager.load_all_plugins(config.gettuple('GENERAL', 'plugins', 'path'),
                                    config.gettuple('GENERAL', 'plugins_disabled', str))

    write_log("Installed plugins: {}".format(", ".join(
        [plugin_manager.get_friendly_name(p) for p in plugin_manager.list_external_plugins()])))

    if not gp:
        write_log("gPhoto2 not installed, cannot diagnose connected DSLR")
        sys.exit(1)

    gp_log_callback = gp.check_result(gp.gp_log_add_func(gp.GP_LOG_VERBOSE, gp_logging))
    write_log("Listing all connected DSLR camera")
    cameras_list = camera_connected()

    if not cameras_list:
        write_log('No compatible DSLR camera detected')
        sys.exit(1)

    cameras_list = sorted(cameras_list, key=lambda x: x[0])
    for index, (name, addr) in enumerate(cameras_list):
        write_log("{:02d} : addr-> {}  name-> {}".format(index, addr, name))

    write_log("Stating diagnostic of connected DSLR camera", True)
    camera = gp.Camera()
    camera.init()

    abilities = camera.get_abilities()
    preview_compat = gp.GP_OPERATION_CAPTURE_PREVIEW ==\
        abilities.operations & gp.GP_OPERATION_CAPTURE_PREVIEW
    write_log("* Preview compatible: {}".format(preview_compat))
    capture_compat = gp.GP_OPERATION_CAPTURE_IMAGE ==\
        abilities.operations & gp.GP_OPERATION_CAPTURE_IMAGE
    write_log("* Capture compatible: {}".format(capture_compat))

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
            image = Image.open(io.BytesIO(camera_file.get_data_and_size()))
            image.save(APPNAME + '.jpg')

        except Exception as ex:
            write_log("ABORT   : exception occures: {}".format(ex), True)
            error = True

    if not error:
        write_log("SUCCESS : diagnostic completed", True)

    del gp_log_callback
    camera.exit()

    write_log("If you are investigating why pibooth does not work with your DSLR camera,")
    write_log("please paste the content of generated file '{}'".format(APPNAME + '.log'))
    write_log("on https://github.com/pibooth/pibooth/issues")
