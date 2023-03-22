#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Pibooth main module.
"""

import os
import os.path as osp
import logging
import pstats
import cProfile

import pygame
from PIL import Image
from gpiozero import ButtonBoard, LEDBoard

import pibooth
from pibooth import view, fonts, language, evts
from pibooth.counters import Counters
from pibooth.states import StateMachine
from pibooth.tasks import AsyncTasksPool
from pibooth.view import get_scene
from pibooth.utils import LOGGER, PollingTimer, get_crash_message, set_logging_level


def load_last_saved_picture(path):
    """Load the saved picture last time pibooth was started.

    :return: PIL.Image instance and path
    :rtype: tuple
    """
    for name in sorted(os.listdir(path), reverse=True):
        filename = osp.join(path, name)
        if osp.isfile(filename) and osp.splitext(name)[-1] == '.jpg':
            return (Image.open(filename), filename)
    return (None, None)


class PiboothApplication(object):

    """Main class representing the ``pibooth`` software.

    The following attributes are available for use in plugins (``app`` reprensents
    the PiboothApplication instance):

    - ``app.capture_nbr`` (int): number of capture to be done in the current sequence
    - ``app.capture_date`` (str): date (% Y-%m-%d-%H-%M-%S) of the first capture of the current sequence
    - ``app.capture_choices``(tuple): possible choices of captures numbers.
    - ``app.previous_picture`` (:py:class:`PIL.Image`): picture generated during last sequence
    - ``app.previous_animated`` (:py:func:`itertools.cycle`): infinite list of picture to display during animation
    - ``app.previous_picture_file`` (str): file name of the picture generated during last sequence
    - ``app.count`` (:py:class:`pibooth.counters.Counters`): holder for counter values
    - ``app.camera`` (:py:class:`pibooth.camera.base.BaseCamera`): camera used
    - ``app.buttons`` (:py:class:`gpiozero.ButtonBoard`): access to hardware buttons ``capture`` and ``printer``
    - ``app.leds`` (:py:class:`gpiozero.LEDBoard`): access to hardware LED ``capture`` and ``printer``
    - ``app.printer`` (:py:class:`pibooth.printer.Printer`): printer used
    """

    def __init__(self, config, plugin_manager, window_type='pygame'):
        self._pm = plugin_manager
        self._config = config
        self._tasks = AsyncTasksPool()

        # Create directories where pictures are saved
        for savedir in config.gettuple('GENERAL', 'directory', 'path'):
            if not osp.isdir(savedir):
                os.makedirs(savedir)

        # Create window of (width, height)
        init_size = self._config.gettyped('WINDOW', 'size')
        init_debug = self._config.getboolean('GENERAL', 'debug')
        init_color = self._config.gettyped('WINDOW', 'background')
        init_text_color = self._config.gettyped('WINDOW', 'text_color')
        if not isinstance(init_color, (tuple, list)):
            init_color = self._config.getpath('WINDOW', 'background')

        title = f"Pibooth v{pibooth.__version__}"
        self._window = view.get_window(window_type, title, init_size, init_color, init_text_color, init_debug)
        self._window.set_menu(self, self._config, self._pm)

        self._multipress_timer = PollingTimer(config.getfloat('CONTROLS', 'multi_press_delay'), False)

        # Define states of the application
        self._machine = StateMachine(self._pm, self._config, self, self._window)
        self._pm.hook.pibooth_setup_states(cfg=self._config, win=self._window, machine=self._machine)

        # ---------------------------------------------------------------------
        # Variables shared with plugins
        # Change them may break plugins compatibility
        self.capture_nbr = None
        self.capture_date = None
        self.capture_choices = (4, 1)

        self.previous_animated = None
        self.previous_picture, self.previous_picture_file = load_last_saved_picture(
            config.gettuple('GENERAL', 'directory', 'path')[0])

        self.count = Counters(self._config.join_path("counters.pickle"),
                              taken=0, printed=0, forgotten=0,
                              remaining_duplicates=self._config.getint('PRINTER', 'max_duplicates'))

        self.camera = self._pm.hook.pibooth_setup_camera(cfg=self._config)

        self.buttons = ButtonBoard(capture="BOARD" + config.get('CONTROLS', 'capture_btn_pin'),
                                   printer="BOARD" + config.get('CONTROLS', 'print_btn_pin'),
                                   hold_time=config.getfloat('CONTROLS', 'debounce_delay'),
                                   pull_up=True)
        self.buttons.capture.when_held = self._on_button_capture_held
        self.buttons.printer.when_held = self._on_button_printer_held

        self.leds = LEDBoard(capture="BOARD" + config.get('CONTROLS', 'capture_led_pin'),
                             printer="BOARD" + config.get('CONTROLS', 'print_led_pin'))

        self.printer = self._pm.hook.pibooth_setup_printer(cfg=self._config)
        self.printer.count = self.count
        # ---------------------------------------------------------------------

    def _initialize(self):
        """Restore the application with initial parameters defined in the
        configuration file.
        Only parameters that can be changed at runtime are restored.
        """
        # Handle the language configuration
        language.set_current(self._config.get('GENERAL', 'language'))
        if self._config.get('WINDOW', 'font').endswith('.ttf') or self._config.get('WINDOW', 'font').endswith('.otf'):
            fonts.CURRENT = fonts.get_filename(self._config.getpath('WINDOW', 'font'))
        else:
            fonts.CURRENT = fonts.get_filename(self._config.get('WINDOW', 'font'))

        # Set the captures choices
        choices = self._config.gettuple('PICTURE', 'captures', int)
        for chx in choices:
            if chx not in [1, 2, 3, 4]:
                LOGGER.warning("Invalid captures number '%s' in config, fallback to '%s'",
                               chx, self.capture_choices)
                choices = self.capture_choices
                break
        self.capture_choices = choices

        # Handle autostart of the application
        self._config.handle_autostart()

        self._window.arrow_location = self._config.get('WINDOW', 'arrows')
        self._window.arrow_offset = self._config.getint('WINDOW', 'arrows_x_offset')
        self._window.text_color = self._config.gettyped('WINDOW', 'text_color')

        # Handle window size
        size = self._config.gettyped('WINDOW', 'size')
        if isinstance(size, str) and size.lower() == 'fullscreen':
            if not self._window.is_fullscreen:
                self._window.toggle_fullscreen()
        else:
            if self._window.is_fullscreen:
                self._window.toggle_fullscreen()
        self._window.debug = self._config.getboolean('GENERAL', 'debug')

        # Handle debug mode
        if not self._config.getboolean('GENERAL', 'debug'):
            set_logging_level()  # Restore default level
            self._machine.add_failsafe_state('failsafe', get_scene(self._window.type, 'failsafe'))
        else:
            set_logging_level(logging.DEBUG)
            self._machine.remove_state('failsafe')

        # Reset the print counter (in case of max_pages is reached)
        self.printer.max_pages = self._config.getint('PRINTER', 'max_pages')

    def _on_button_capture_held(self):
        """Called when the capture button is pressed.
        """
        if all(self.buttons.value):
            self.buttons.capture.hold_repeat = True
            if self._multipress_timer.elapsed() == 0:
                self._multipress_timer.start()
            if self._multipress_timer.is_timeout():
                # Capture was held while printer was pressed
                self.buttons.capture.hold_repeat = False
                self._multipress_timer.reset()
                LOGGER.debug("Event triggered: EVT_BUTTON_SETTINGS")
                evts.post(evts.EVT_BUTTON_SETTINGS, buttons=self.buttons, leds=self.leds)
        else:
            # Capture was held but printer not pressed
            self.buttons.capture.hold_repeat = False
            self._multipress_timer.reset()
            LOGGER.debug("Event triggered: EVT_BUTTON_CAPTURE")
            evts.post(evts.EVT_BUTTON_CAPTURE, buttons=self.buttons, leds=self.leds)

    def _on_button_printer_held(self):
        """Called when the printer button is pressed.
        """
        if all(self.buttons.value):
            # Printer was held while capture was pressed
            # but don't do anything here, let capture_held handle it instead
            pass
        else:
            # Printer was held but capture not pressed
            LOGGER.debug("Event triggered: EVT_BUTTON_PRINT")
            evts.post(evts.EVT_BUTTON_PRINT, buttons=self.buttons, leds=self.leds)

    @property
    def picture_filename(self):
        """Return the final picture file name.
        """
        if not self.capture_date:
            raise EnvironmentError("The 'capture_date' attribute is not set yet")
        return f"{self.capture_date}_pibooth.jpg"

    def enable_plugin(self, plugin):
        """Enable plugin with given name. The "configure" and "startup" hooks will
        be called if never done before.

        :param plugin: plugin to disable
        :type plugin: object
        """
        if not self._pm.is_registered(plugin):
            self._pm.register(plugin)
            LOGGER.debug("Plugin '%s' enable", self._pm.get_name(plugin))
            # Because no hook is called for plugins disabled at pibooth startup, need to
            # ensure that mandatory hooks have been called when enabling a plugin
            if 'pibooth_configure' not in self._pm.get_calls_history(plugin):
                hook = self._pm.subset_hook_caller_for_plugin('pibooth_configure', plugin)
                hook(cfg=self._config)
            if 'pibooth_startup' not in self._pm.get_calls_history(plugin):
                hook = self._pm.subset_hook_caller_for_plugin('pibooth_startup', plugin)
                hook(cfg=self._config, app=self)

    def disable_plugin(self, plugin):
        """Disable plugin with given name.

        :param plugin: plugin to disable
        :type plugin: object
        """
        if self._pm.is_registered(plugin):
            LOGGER.debug("Plugin '%s' disabled", self._pm.get_name(plugin))
            self._pm.unregister(plugin)

    def update(self, events):
        """Update application and call plugins according to Pygame events.
        Better to call it in the main thread to avoid plugin thread-safe issues.

        :param events: list of events to process.
        :type events: list
        """
        if evts.find_event(events, evts.EVT_PIBOOTH_SETTINGS):
            if self._window.is_menu_shown:  # Settings menu is opened
                self.camera.stop_preview()
                self.leds.off()
                self.leds.blink(on_time=0.1, off_time=1)
            elif not self._window.is_menu_shown:  # Settings menu is closed
                self.leds.off()
                self._initialize()
                self._machine.set_state('wait')
        else:
            self._machine.process(events)

    def exec(self, enable_profiler=False):
        """Start application.
        """
        if enable_profiler:
            profiler = cProfile.Profile()

        try:
            self._initialize()
            self._pm.hook.pibooth_startup(cfg=self._config, app=self)
            self._machine.set_state('wait')
            if enable_profiler:
                profiler.enable()
            self._window.eventloop(self.update)
        except KeyboardInterrupt:
            print()
        except Exception as ex:
            LOGGER.error(str(ex), exc_info=True)
            LOGGER.error(get_crash_message())
        finally:

            if enable_profiler:
                stats = pstats.Stats(profiler).sort_stats('cumtime')
                stats.print_stats()
                profiler.disable()

            self._pm.hook.pibooth_cleanup(app=self)
            self._tasks.quit()
            pygame.quit()
