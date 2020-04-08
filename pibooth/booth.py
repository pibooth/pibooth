#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Pibooth main module.
"""

import os
import shutil
import logging
import argparse
import os.path as osp
import pygame
import pluggy
import pibooth
from pibooth import fonts
from pibooth import language
from pibooth.utils import (LOGGER, configure_logging,
                           set_logging_level, print_columns_words)
from pibooth.states import StateMachine
from pibooth.plugins import hookspecs, load_plugins
from pibooth.view import PtbWindow
from pibooth.config import PiConfigParser, PiConfigMenu
from pibooth.controls import GPIO, camera
from pibooth.fonts import get_available_fonts
from pibooth.controls.light import PtbLed
from pibooth.controls.button import BUTTON_DOWN, PtbButton
from pibooth.controls.printer import PRINTER_TASKS_UPDATED, PtbPrinter


class PiApplication(object):

    def __init__(self, config):
        self._config = config

        # Clean directory where pictures are saved
        savedir = config.getpath('GENERAL', 'directory')
        if not osp.isdir(savedir):
            os.makedirs(savedir)
        elif osp.isdir(savedir) and config.getboolean('GENERAL', 'debug'):
            shutil.rmtree(savedir)
            os.makedirs(savedir)

        # Prepare GPIO, physical pins mode
        GPIO.setmode(GPIO.BOARD)

        # Prepare the pygame module for use
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        pygame.init()
        # Dont catch mouse motion to avoid filling the queue during long actions
        pygame.event.set_blocked(pygame.MOUSEMOTION)

        # Create window of (width, height)
        init_size = self._config.gettyped('WINDOW', 'size')
        init_debug = self._config.getboolean('GENERAL', 'debug')
        init_color = self._config.gettyped('WINDOW', 'background')
        init_text_color = self._config.gettyped('WINDOW', 'text_color')
        if not isinstance(init_color, (tuple, list)):
            init_color = self._config.getpath('WINDOW', 'background')

        title = 'Pibooth v{}'.format(pibooth.__version__)
        if not isinstance(init_size, str):
            self._window = PtbWindow(title, init_size, color=init_color,
                                     text_color=init_text_color, debug=init_debug)
        else:
            self._window = PtbWindow(title, color=init_color,
                                     text_color=init_text_color, debug=init_debug)

        # Create plugin manager and defined hooks specification
        self._plugin_manager = pluggy.PluginManager(hookspecs.hookspec.project_name)
        self._plugin_manager.add_hookspecs(hookspecs)
        self._plugin_manager.load_setuptools_entrypoints(hookspecs.hookspec.project_name)

        # Register plugins
        custom_paths = [p for p in self._config.gettuple('GENERAL', 'plugins', 'path') if p]
        load_plugins(self._plugin_manager, *custom_paths)

        # Define states of the application
        self._machine = StateMachine(self._plugin_manager, self._config, self, self._window)
        self._machine.add_state('wait')
        self._machine.add_state('choose')
        self._machine.add_state('chosen')
        self._machine.add_state('preview')
        self._machine.add_state('capture')
        self._machine.add_state('processing')
        self._machine.add_state('print')
        self._machine.add_state('finish')

        self.camera = camera.get_camera(config.getint('CAMERA', 'iso'),
                                        config.gettyped('CAMERA', 'resolution'),
                                        config.getint('CAMERA', 'rotation'),
                                        config.getboolean('CAMERA', 'flip'),
                                        config.getboolean('CAMERA', 'delete_internal_memory'))

        # Initialize the hardware buttons
        self.led_capture = PtbLed(config.getint('CONTROLS', 'picture_led_pin'))
        self.button_capture = PtbButton(config.getint('CONTROLS', 'picture_btn_pin'),
                                        config.getfloat('CONTROLS', 'debounce_delay'))

        self.led_print = PtbLed(config.getint('CONTROLS', 'print_led_pin'))
        self.button_print = PtbButton(config.getint('CONTROLS', 'print_btn_pin'),
                                      config.getfloat('CONTROLS', 'debounce_delay'))

        self.led_startup = PtbLed(config.getint('CONTROLS', 'startup_led_pin'))
        self.led_preview = PtbLed(config.getint('CONTROLS', 'preview_led_pin'))

        # Initialize the printer
        self.printer = PtbPrinter(config.get('PRINTER', 'printer_name'))

        # ---------------------------------------------------------------------
        # Variables shared with plugins
        self.dirname = None
        self.capture_nbr = None
        self.capture_choices = (4, 1)
        self.nbr_duplicates = 0
        self.previous_picture = None
        self.previous_animated = None
        self.previous_picture_file = None
        # ---------------------------------------------------------------------

    def _initialize(self):
        """Restore the application with initial parameters defined in the
        configuration file.
        Only parameters that can be changed at runtime are restored.
        """
        # Handle the language configuration
        language.CURRENT = self._config.get('GENERAL', 'language')
        fonts.CURRENT = fonts.get_filename(self._config.gettuple('PICTURE', 'text_fonts', str)[0])

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
        self._config.enable_autostart(self._config.getboolean('GENERAL', 'autostart'))

        self._window.arrow_location = self._config.get('WINDOW', 'arrows')
        self._window.arrow_offset = self._config.getint('WINDOW', 'arrows_x_offset')
        self._window.text_color = self._config.gettyped('WINDOW', 'text_color')
        self._window.drop_cache()

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

        # Initialize state machine
        self._machine.set_state('wait')

    @property
    def printer_unavailable(self):
        """Return True is paper/ink counter is reached or printing is disabled
        """
        if self._config.getint('PRINTER', 'max_pages') < 0:  # No limit
            return False
        return self.printer.nbr_printed >= self._config.getint('PRINTER', 'max_pages')

    def find_quit_event(self, events):
        """Return the first found event if found in the list.
        """
        for event in events:
            if event.type == pygame.QUIT:
                return event
        return None

    def find_settings_event(self, events, type_filter=None):
        """Return the first found event if found in the list.
        """
        event_capture = None
        event_print = None
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE and \
                    (type_filter is None or type_filter == event.type):
                return event
            if event.type == BUTTON_DOWN:
                if event.pin == self.button_capture and (type_filter is None or type_filter == event.type):
                    event_capture = event
                elif event.pin == self.button_print and (type_filter is None or type_filter == event.type):
                    event_print = event
            if event_capture and event_print:
                return event_capture  # One of both (return != None is enough)

        return None

    def find_fullscreen_event(self, events):
        """Return the first found event if found in the list.
        """
        for event in events:
            if event.type == pygame.KEYDOWN and \
                    event.key == pygame.K_f and pygame.key.get_mods() & pygame.KMOD_CTRL:
                return event
        return None

    def find_resize_event(self, events):
        """Return the first found event if found in the list.
        """
        for event in events:
            if event.type == pygame.VIDEORESIZE:
                return event
        return None

    def find_capture_event(self, events, type_filter=None):
        """Return the first found event if found in the list.
        """
        for event in events:
            if (event.type == pygame.KEYDOWN and event.key == pygame.K_p) or \
                    (event.type == BUTTON_DOWN and event.pin == self.button_capture):
                if type_filter is None or type_filter == event.type:
                    return event
            elif event.type == pygame.MOUSEBUTTONUP:
                rect = self._window.get_rect()
                if pygame.Rect(0, 0, rect.width // 2, rect.height).collidepoint(event.pos):
                    if type_filter is None or type_filter == event.type:
                        return event
        return None

    def find_print_event(self, events, type_filter=None):
        """Return the first found event if found in the list.
        """
        for event in events:
            if (event.type == pygame.KEYDOWN and event.key == pygame.K_e and
                    pygame.key.get_mods() & pygame.KMOD_CTRL) or \
                    (event.type == BUTTON_DOWN and event.pin == self.button_print):
                if type_filter is None or type_filter == event.type:
                    return event
            elif event.type == pygame.MOUSEBUTTONUP:
                rect = self._window.get_rect()
                if pygame.Rect(rect.width // 2, 0, rect.width // 2, rect.height).collidepoint(event.pos):
                    if type_filter is None or type_filter == event.type:
                        return event
        return None

    def find_print_status_event(self, events):
        """Return the first found event if found in the list.
        """
        for event in events:
            if event.type == PRINTER_TASKS_UPDATED:
                return event
        return None

    def find_choice_event(self, events):
        """Return the first found event if found in the list.
        """
        for event in events:
            if (event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT) or \
                    (event.type == BUTTON_DOWN and event.pin == self.button_capture):
                event.key = pygame.K_LEFT
                return event
            elif (event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT) or \
                    (event.type == BUTTON_DOWN and event.pin == self.button_print):
                event.key = pygame.K_RIGHT
                return event
            elif event.type == pygame.MOUSEBUTTONUP:
                rect = self._window.get_rect()
                if pygame.Rect(0, 0, rect.width // 2, rect.height).collidepoint(event.pos):
                    event.key = pygame.K_LEFT
                else:
                    event.key = pygame.K_RIGHT
                return event
        return None

    def main_loop(self):
        """Run the main game loop.
        """
        try:
            clock = pygame.time.Clock()
            self._initialize()
            self._plugin_manager.hook.pibooth_startup(app=self)
            menu = None
            fps = 40

            while True:
                events = list(pygame.event.get())

                if self.find_quit_event(events):
                    break

                if self.find_fullscreen_event(events):
                    self._window.toggle_fullscreen()

                event = self.find_resize_event(events)
                if event:
                    self._window.resize(event.size)

                if not menu and self.find_settings_event(events):
                    menu = PiConfigMenu(self._window, self._config, fps, version=pibooth.__version__)
                    menu.show()

                if menu and menu.is_shown():
                    # Convert HW button events to keyboard events for menu
                    if self.find_settings_event(events, BUTTON_DOWN):
                        events.insert(0, menu.create_back_event())
                    if self.find_capture_event(events, BUTTON_DOWN):
                        events.insert(0, menu.create_next_event())
                    elif self.find_print_event(events, BUTTON_DOWN):
                        events.insert(0, menu.create_click_event())
                    menu.process(events)
                elif menu and not menu.is_shown():
                    self._initialize()
                    menu = None
                else:
                    self._machine.process(events)

                pygame.display.update()
                clock.tick(fps)  # Ensure the program will never run at more than <fps> frames per second

        finally:
            self._plugin_manager.hook.pibooth_cleanup(app=self)
            GPIO.cleanup()
            pygame.quit()


def main():
    """Application entry point.
    """
    parser = argparse.ArgumentParser(usage="%(prog)s [options]", description=pibooth.__doc__)

    parser.add_argument('--version', action='version', version=pibooth.__version__,
                        help=u"show program's version number and exit")

    parser.add_argument("--config", action='store_true',
                        help=u"edit the current configuration and exit")

    parser.add_argument("--translate", action='store_true',
                        help=u"edit the GUI translations and exit")

    parser.add_argument("--reset", action='store_true',
                        help=u"restore the default configuration/translations and exit")

    parser.add_argument("--fonts", action='store_true',
                        help=u"display all available fonts and exit")

    parser.add_argument("--log", default=None,
                        help=u"save logs output to the given file")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("-v", "--verbose", dest='logging', action='store_const', const=logging.DEBUG,
                       help=u"report more information about operations", default=logging.INFO)
    group.add_argument("-q", "--quiet", dest='logging', action='store_const', const=logging.WARNING,
                       help=u"report only errors and warnings", default=logging.INFO)

    options, _args = parser.parse_known_args()

    configure_logging(options.logging, '[ %(levelname)-8s] %(name)-18s: %(message)s', filename=options.log)

    config = PiConfigParser("~/.config/pibooth/pibooth.cfg", options.reset)
    language.init("~/.config/pibooth/translations.cfg", options.reset)

    if options.config:
        LOGGER.info("Editing the pibooth configuration...")
        config.edit()
    elif options.translate:
        LOGGER.info("Editing the GUI translations...")
        language.edit()
    elif options.fonts:
        LOGGER.info("Listing all fonts available...")
        print_columns_words(get_available_fonts(), 3)
    elif not options.reset:
        LOGGER.info("Starting the photo booth application...")
        app = PiApplication(config)
        app.main_loop()


if __name__ == '__main__':
    main()
