#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Pibooth main module.
"""

import os
import os.path as osp
import shutil
import logging
import argparse
from warnings import filterwarnings

import pygame
from gpiozero import Device, ButtonBoard, LEDBoard, pi_info
from gpiozero.exc import BadPinFactory, PinFactoryFallback

import pibooth
from pibooth import fonts
from pibooth import language
from pibooth.counters import Counters
from pibooth.utils import (LOGGER, configure_logging,
                           set_logging_level, print_columns_words)
from pibooth.states import StateMachine
from pibooth.plugins import create_plugin_manager, load_plugins, list_plugin_names
from pibooth.view import PtbWindow
from pibooth.config import PiConfigParser, PiConfigMenu
from pibooth import camera
from pibooth.fonts import get_available_fonts
from pibooth.printer import PRINTER_TASKS_UPDATED, Printer


# Set the default pin factory to a mock factory if pibooth is not started a Raspberry Pi
try:
    filterwarnings("ignore", category=PinFactoryFallback)
    GPIO_INFO = "on Raspberry pi {0}".format(pi_info().model)
except BadPinFactory:
    from gpiozero.pins.mock import MockFactory
    Device.pin_factory = MockFactory()
    GPIO_INFO = "without physical GPIO, fallback to GPIO mock"


BUTTONDOWN = pygame.USEREVENT + 1


class PiApplication(object):

    def __init__(self, config, plugin_manager):
        self._pm = plugin_manager
        self._config = config

        # Create directories where pictures are saved
        for savedir in config.gettuple('GENERAL', 'directory', 'path'):
            if osp.isdir(savedir) and config.getboolean('GENERAL', 'debug'):
                shutil.rmtree(savedir)
            if not osp.isdir(savedir):
                os.makedirs(savedir)

        # Prepare the pygame module for use
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        pygame.init()

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

        self._menu = None

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
        self.previous_picture = None
        self.previous_animated = None
        self.previous_picture_file = None

        self.count = Counters(self._config.join_path("counters.pickle"),
                              taken=0, printed=0, forgotten=0,
                              remaining_duplicates=self._config.getint('PRINTER', 'max_duplicates'))

        self.camera = camera.get_camera(config.getint('CAMERA', 'iso'),
                                        config.gettyped('CAMERA', 'resolution'),
                                        config.getint('CAMERA', 'rotation'),
                                        config.getboolean('CAMERA', 'flip'),
                                        config.getboolean('CAMERA', 'delete_internal_memory'))

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
                               self.count)
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
        self._config.handle_autostart()

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

        # Reset the print counter (in case of max_pages is reached)
        self.printer.max_pages = self._config.getint('PRINTER', 'max_pages')

    def _on_button_capture_held(self):
        """Called when the capture button is pressed.
        """
        if all(self.buttons.value):
            # capture was held while printer was pressed
            if self._menu and self._menu.is_shown():
                # Convert HW button events to keyboard events for menu
                event = self._menu.create_back_event()
                LOGGER.debug("BUTTONDOWN: generate MENU-ESC event")
            else:
                event = pygame.event.Event(BUTTONDOWN, capture=1, printer=1,
                                           button=self.buttons)
                LOGGER.debug("BUTTONDOWN: generate DOUBLE buttons event")
        else:
            # capture was held but printer not pressed
            if self._menu and self._menu.is_shown():
                # Convert HW button events to keyboard events for menu
                event = self._menu.create_next_event()
                LOGGER.debug("BUTTONDOWN: generate MENU-NEXT event")
            else:
                event = pygame.event.Event(BUTTONDOWN, capture=1, printer=0,
                                           button=self.buttons.capture)
                LOGGER.debug("BUTTONDOWN: generate CAPTURE button event")
        pygame.event.post(event)

    def _on_button_printer_held(self):
        """Called when the printer button is pressed.
        """
        if all(self.buttons.value):
            # printer was held while capture was pressed
            # but don't do anything here, let capture_held handle it instead
            pass
        else:
            # printer was held but capture not pressed
            if self._menu and self._menu.is_shown():
                # Convert HW button events to keyboard events for menu
                event = self._menu.create_click_event()
                LOGGER.debug("BUTTONDOWN: generate MENU-APPLY event")
            else:
                event = pygame.event.Event(BUTTONDOWN, capture=0, printer=1,
                                           button=self.buttons.printer)
                LOGGER.debug("BUTTONDOWN: generate PRINTER event")
            pygame.event.post(event)

    @property
    def picture_filename(self):
        """Return the final picture file name.
        """
        if not self.capture_date:
            raise EnvironmentError("The 'capture_date' attribute is not set yet")
        return "{}_pibooth.jpg".format(self.capture_date)

    def find_quit_event(self, events):
        """Return the first found event if found in the list.
        """
        for event in events:
            if event.type == pygame.QUIT:
                return event
        return None

    def find_settings_event(self, events):
        """Return the first found event if found in the list.
        """
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return event
            if event.type == BUTTONDOWN and event.capture and event.printer:
                return event
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

    def find_capture_event(self, events):
        """Return the first found event if found in the list.
        """
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                return event
            if event.type == pygame.MOUSEBUTTONUP and event.button in (1, 2, 3):
                # Don't consider the mouse wheel (button 4 & 5):
                rect = self._window.get_rect()
                if pygame.Rect(0, 0, rect.width // 2, rect.height).collidepoint(event.pos):
                    return event
            if event.type == BUTTONDOWN and event.capture:
                return event
        return None

    def find_print_event(self, events):
        """Return the first found event if found in the list.
        """
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_e\
                        and pygame.key.get_mods() & pygame.KMOD_CTRL:
                return event
            if event.type == pygame.MOUSEBUTTONUP and event.button in (1, 2, 3):
                # Don't consider the mouse wheel (button 4 & 5):
                rect = self._window.get_rect()
                if pygame.Rect(rect.width // 2, 0, rect.width // 2, rect.height).collidepoint(event.pos):
                    return event
            if event.type == BUTTONDOWN and event.printer:
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
            if event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
                return event
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
                return event
            if event.type == pygame.MOUSEBUTTONUP and event.button in (1, 2, 3):
                # Don't consider the mouse wheel (button 4 & 5):
                rect = self._window.get_rect()
                if pygame.Rect(0, 0, rect.width // 2, rect.height).collidepoint(event.pos):
                    event.key = pygame.K_LEFT
                else:
                    event.key = pygame.K_RIGHT
                return event
            if event.type == BUTTONDOWN:
                if event.capture:
                    event.key = pygame.K_LEFT
                else:
                    event.key = pygame.K_RIGHT
                return event
        return None

    def main_loop(self):
        """Run the main game loop.
        """
        try:
            fps = 40
            clock = pygame.time.Clock()
            self._initialize()
            self._pm.hook.pibooth_startup(cfg=self._config, app=self)
            self._machine.set_state('wait')

            while True:
                events = list(pygame.event.get())

                if self.find_quit_event(events):
                    break

                if self.find_fullscreen_event(events):
                    self._window.toggle_fullscreen()

                event = self.find_resize_event(events)
                if event:
                    self._window.resize(event.size)

                if not self._menu and self.find_settings_event(events):
                    self.leds.off()
                    self._menu = PiConfigMenu(self._window, self._config, self.count)
                    self._menu.show()
                    self.leds.blink(on_time=0.1, off_time=1)
                elif self._menu and self._menu.is_shown():
                    self._menu.process(events)
                elif self._menu and not self._menu.is_shown():
                    self.leds.off()
                    self._initialize()
                    self._machine.set_state('wait')
                    self._menu = None
                else:
                    self._machine.process(events)

                pygame.display.update()
                clock.tick(fps)  # Ensure the program will never run at more than <fps> frames per second

        finally:
            self._pm.hook.pibooth_cleanup(app=self)
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

    plugin_manager = create_plugin_manager()

    # Load the configuration and languages
    config = PiConfigParser("~/.config/pibooth/pibooth.cfg", plugin_manager)
    language.init(config.join_path("translations.cfg"), options.reset)

    # Register plugins
    custom_paths = [p for p in config.gettuple('GENERAL', 'plugins', 'path') if p]
    load_plugins(plugin_manager, *custom_paths)
    LOGGER.info("Installed plugins: %s", ", ".join(list_plugin_names(plugin_manager)))

    # Update configuration with plugins ones
    plugin_manager.hook.pibooth_configure(cfg=config)

    # Ensure config files are present in case of first pibooth launch
    if not options.reset:
        if not osp.isfile(config.filename):
            config.save(default=True)
        plugin_manager.hook.pibooth_reset(cfg=config, hard=False)

    if options.config:
        LOGGER.info("Editing the pibooth configuration...")
        config.edit()
    elif options.translate:
        LOGGER.info("Editing the GUI translations...")
        language.edit()
    elif options.fonts:
        LOGGER.info("Listing all fonts available...")
        print_columns_words(get_available_fonts(), 3)
    elif options.reset:
        config.save(default=True)
        plugin_manager.hook.pibooth_reset(cfg=config, hard=True)
    else:
        LOGGER.info("Starting the photo booth application %s", GPIO_INFO)
        app = PiApplication(config, plugin_manager)
        app.main_loop()


if __name__ == '__main__':
    main()
