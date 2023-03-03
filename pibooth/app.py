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
from pibooth.printer import Printer
from pibooth.tasks import AsyncTasksPool
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
    The following attributes are available for use in plugins:

    : attr capture_nbr: number of capture to be done in the current sequence
    : type capture_nbr: int
    : attr capture_date: date (% Y-%m-%d-%H-%M-%S) of the first capture of the current sequence
    : type capture_date: str
    : attr capture_choices: possible choices of captures numbers.
    : type capture_choices: tuple
    : attr previous_picture: picture generated during last sequence
    : type previous_picture: : py: class: `PIL.Image`
    : attr previous_animated: infinite list of picture to display during animation
    : type previous_animated: : py: func: `itertools.cycle`
    : attr previous_picture_file: file name of the picture generated during last sequence
    : type previous_picture_file: str
    : attr count: holder for counter values
    : type count: : py: class: `pibooth.counters.Counters`
    : attr camera: camera used
    : type camera: : py: class: `pibooth.camera.base.BaseCamera`
    : attr buttons: access to hardware buttons ``capture`` and ``printer``
    : type buttons: : py: class: `gpiozero.ButtonBoard`
    : attr leds: access to hardware LED ``capture`` and ``printer``
    : attr leds: : py: class: `gpiozero.LEDBoard`
    : attr printer: printer used
    : type printer: : py: class: `pibooth.printer.Printer`
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

        title = 'Pibooth v{}'.format(pibooth.__version__)
        self._window = view.get_window(window_type, title, init_size, init_color, init_text_color, init_debug)
        self._window.set_menu(self, self._config, self._pm)

        self._multipress_timer = PollingTimer(config.getfloat('CONTROLS', 'multi_press_delay'), False)

        # Define states of the application
        self._machine = StateMachine(self._pm, self._config, self, self._window)
        self._machine.add_state('wait')
        self._machine.add_state('choose')
        self._machine.add_state('chosen')
        self._machine.add_state('preview')
        self._machine.add_state('capture')
        self._machine.add_state('processing')
        self._machine.add_state('print')
        self._machine.add_state('finish')

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

        self.buttons = ButtonBoard(capture="BOARD" + config.get('CONTROLS', 'picture_btn_pin'),
                                   printer="BOARD" + config.get('CONTROLS', 'print_btn_pin'),
                                   hold_time=config.getfloat('CONTROLS', 'debounce_delay'),
                                   pull_up=True)
        self.buttons.capture.when_held = self._on_button_capture_held
        self.buttons.printer.when_held = self._on_button_printer_held

        self.leds = LEDBoard(capture="BOARD" + config.get('CONTROLS', 'picture_led_pin'),
                             printer="BOARD" + config.get('CONTROLS', 'print_led_pin'))

        self.printer = Printer(config.get('PRINTER', 'printer_name'),
                               config.getint('PRINTER', 'max_pages'),
                               config.gettyped('PRINTER', 'printer_options'),
                               self.count)
        # ---------------------------------------------------------------------

    def _initialize(self):
        """Restore the application with initial parameters defined in the
        configuration file.
        Only parameters that can be changed at runtime are restored.
        """
        # Handle the language configuration
        language.CURRENT = self._config.get('GENERAL', 'language')
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
            self._machine.add_failsafe_state('failsafe')
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
                evts.post_button_settings_event()
        else:
            # Capture was held but printer not pressed
            self.buttons.capture.hold_repeat = False
            self._multipress_timer.reset()
            evts.post_button_capture_event()

    def _on_button_printer_held(self):
        """Called when the printer button is pressed.
        """
        if all(self.buttons.value):
            # Printer was held while capture was pressed
            # but don't do anything here, let capture_held handle it instead
            pass
        else:
            # Printer was held but capture not pressed
            evts.post_button_print_event()

    @property
    def picture_filename(self):
        """Return the final picture file name.
        """
        if not self.capture_date:
            raise EnvironmentError("The 'capture_date' attribute is not set yet")
        return "{}_pibooth.jpg".format(self.capture_date)

    def update(self, events):
        """Update application and call plugins according to Pygame events.
        Better to call it in the main thread to avoid plugin thread-safe issues.

        :param events: list of events to process.
        :type events: list
        """
        if evts.find_event(events, evts.EVT_PIBOOTH_BTN_SETTINGS):
            if not self._window.is_menu_shown:  # Settings menu is opened
                self.camera.stop_preview()
                self.leds.off()
                self.leds.blink(on_time=0.1, off_time=1)
            elif self._window.is_menu_shown:  # Settings menu is closed
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
