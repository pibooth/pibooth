#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Pibooth main module.
"""

import os
import time
import shutil
import logging
import argparse
import os.path as osp
import pygame
from RPi import GPIO
from PIL import Image
import pibooth
from pibooth.utils import (LOGGER, timeit, PoolingTimer,
                           configure_logging, print_columns_words)
from pibooth.states import StateMachine, State
from pibooth.view import PtbWindow
from pibooth.config.parser import PiConfigParser, get_supported_languages
from pibooth.config.menu import PiConfigMenu
from pibooth.controls import camera
from pibooth.fonts import get_available_fonts
from pibooth.pictures.concatenate import concatenate_pictures
from pibooth.controls.light import PtbLed
from pibooth.controls.button import BUTTON_DOWN, PtbButton
from pibooth.controls.printer import PRINTER_TASKS_UPDATED, PtbPrinter


class StateFailSafe(State):

    def __init__(self, timeout):
        State.__init__(self, 'failsafe')
        self.timer = PoolingTimer(timeout)

    def entry_actions(self):
        self.app.dirname = None
        self.app.nbr_captures = None
        self.app.nbr_printed = 0
        self.app.camera.drop_captures()  # Flush previous captures
        self.app.window.show_oops()
        self.timer.start()

    def validate_transition(self, events):
        if self.timer.is_timeout():
            return 'wait'


class StateWait(State):

    def __init__(self):
        State.__init__(self, 'wait')

    def entry_actions(self):
        self.app.window.show_intro(self.app.previous_picture, self.app.printer.is_installed() and
                                   self.app.nbr_printed < self.app.config.getint('PRINTER', 'max_duplicates'))
        self.app.led_picture.blink()
        if self.app.previous_picture_file and self.app.printer.is_installed():
            self.app.led_print.blink()

    def do_actions(self, events):
        if self.app.find_print_event(events) and self.app.previous_picture_file and self.app.printer.is_installed():

            if self.app.nbr_printed >= self.app.config.getint('PRINTER', 'max_duplicates'):
                LOGGER.warning("Too many duplicates sent to the printer (%s max)",
                               self.app.config.getint('PRINTER', 'max_duplicates'))
                return

            with timeit("Send final picture to printer"):
                self.app.led_print.switch_on()
                self.app.printer.print_file(self.app.previous_picture_file,
                                            self.app.config.getint('PRINTER', 'nbr_copies'))

            time.sleep(1)  # Just to let the LED switched on
            self.app.nbr_printed += 1

            if self.app.nbr_printed >= self.app.config.getint('PRINTER', 'max_duplicates'):
                self.app.window.show_intro(self.app.previous_picture, False)
                self.app.led_print.switch_off()
            else:
                self.app.led_print.blink()

        event = self.app.find_print_status_event(events)
        if event:
            self.app.window.set_print_number(len(event.tasks))

    def exit_actions(self):
        self.app.led_picture.switch_off()
        self.app.led_print.switch_off()

        # Clear currently displayed image
        self.app.window.show_image(None)

    def validate_transition(self, events):
        if self.app.find_picture_event(events):
            if len(self.app.capture_choices) > 1:
                return 'choose'
            else:
                self.app.nbr_captures = self.app.capture_choices[0]
                return 'capture'


class StateChoose(State):

    def __init__(self, timeout):
        State.__init__(self, 'choose')
        self.timer = PoolingTimer(timeout)

    def entry_actions(self):
        with timeit("Show picture choice (nothing selected)"):
            self.app.window.set_print_number(0)  # Hide printer status
            self.app.window.show_choice(self.app.capture_choices)
        self.app.nbr_captures = None
        self.app.led_picture.blink()
        self.app.led_print.blink()
        self.timer.start()

    def do_actions(self, events):
        event = self.app.find_choice_event(events)
        if event:
            if event.key == pygame.K_LEFT:
                self.app.nbr_captures = self.app.capture_choices[0]
            elif event.key == pygame.K_RIGHT:
                self.app.nbr_captures = self.app.capture_choices[1]

    def exit_actions(self):
        if self.app.nbr_captures == self.app.capture_choices[0]:
            self.app.led_picture.switch_on()
            self.app.led_print.switch_off()
        elif self.app.nbr_captures == self.app.capture_choices[1]:
            self.app.led_print.switch_on()
            self.app.led_picture.switch_off()
        else:
            self.app.led_print.switch_off()
            self.app.led_picture.switch_off()

    def validate_transition(self, events):
        if self.app.nbr_captures:
            return 'chosen'
        elif self.timer.is_timeout():
            return 'wait'


class StateChosen(State):

    def __init__(self, timeout):
        State.__init__(self, 'chosen')
        self.timer = PoolingTimer(timeout)

    def entry_actions(self):
        with timeit("Show picture choice ({} pictures selected)".format(self.app.nbr_captures)):
            self.app.window.show_choice(self.app.capture_choices, selected=self.app.nbr_captures)
        self.timer.start()

    def exit_actions(self):
        self.app.led_picture.switch_off()
        self.app.led_print.switch_off()

    def validate_transition(self, events):
        if self.timer.is_timeout():
            return 'capture'


class StateCapture(State):

    def __init__(self):
        State.__init__(self, 'capture')
        self.count = 0

    def entry_actions(self):
        LOGGER.info("Start new pictures sequence")
        self.app.nbr_printed = 0
        self.app.previous_picture = None
        self.app.previous_picture_file = None
        self.app.dirname = osp.join(self.app.savedir, "raw", time.strftime("%Y-%m-%d-%H-%M-%S"))
        os.makedirs(self.app.dirname)
        self.app.led_preview.switch_on()

        self.count = 0
        self.app.window.set_picture_number(self.count, self.app.nbr_captures)
        self.app.camera.preview(self.app.window)

    def do_actions(self, events):
        self.app.window.set_picture_number(self.count + 1, self.app.nbr_captures)
        pygame.event.pump()

        if self.app.config.getboolean('WINDOW', 'preview_countdown'):
            self.app.camera.preview_countdown(self.app.config.getint('WINDOW', 'preview_delay'))
        else:
            self.app.camera.preview_wait(self.app.config.getint('WINDOW', 'preview_delay'))

        capture_path = osp.join(self.app.dirname, "pibooth{:03}.jpg".format(self.count))

        if self.app.config.getboolean('WINDOW', 'preview_stop_on_capture'):
            self.app.camera.stop_preview()

        effects = self.app.config.gettyped('PICTURE', 'effect')
        if not isinstance(effects, (list, tuple)):
            # Same effect for all captures
            effect = effects
        elif len(effects) >= self.app.nbr_captures:
            # Take the effect corresponding to the current capture
            effect = effects[self.count]
        else:
            # Not possible
            raise ValueError("Not enough effects defined for {} captures {}".format(
                self.app.nbr_captures, effects))

        with timeit("Take picture and save it in {}".format(capture_path)):
            if self.app.config.getboolean('WINDOW', 'flash'):
                with self.app.window.flash(2):
                    self.app.camera.capture(capture_path, effect)
            else:
                self.app.camera.capture(capture_path, effect)

        self.count += 1

        if self.app.config.getboolean('WINDOW', 'preview_stop_on_capture') and self.count < self.app.nbr_captures:
            # Restart preview only if other captures needed
            self.app.camera.preview(self.app.window)

    def exit_actions(self):
        self.app.camera.stop_preview()
        self.app.led_preview.switch_off()

    def validate_transition(self, events):
        if self.count >= self.app.nbr_captures:
            return 'processing'


class StateProcessing(State):

    def __init__(self):
        State.__init__(self, 'processing')

    def entry_actions(self):
        self.app.window.show_work_in_progress()

    def do_actions(self, events):
        with timeit("Creating merged picture"):
            footer_texts = [self.app.config.get('PICTURE', 'footer_text1'),
                            self.app.config.get('PICTURE', 'footer_text2')]
            bg_color = self.app.config.gettyped('PICTURE', 'bg_color')

            if not isinstance(bg_color, (tuple, list)):
                # Path to a background image
                bg_color = Image.open(self.app.config.getpath('PICTURE', 'bg_color'))
            text_color = self.app.config.gettyped('PICTURE', 'text_color')
            orientation = self.app.config.get('PICTURE', 'orientation')

            footer_fonts = self.app.config.gettyped('PICTURE', 'fonts')
            if isinstance(footer_fonts, str):
                # Apply same font on both footers
                footer_fonts = (footer_fonts, footer_fonts)
            elif len(footer_fonts) < 2:
                # Apply same font on both footers
                footer_fonts = (footer_fonts[0], footer_fonts[0])
            self.app.previous_picture = concatenate_pictures(self.app.camera.get_captures(),
                                                             footer_texts,
                                                             footer_fonts,
                                                             bg_color, text_color,
                                                             orientation)

        self.app.previous_picture_file = osp.join(
            self.app.savedir, osp.basename(self.app.dirname) + "_pibooth.jpg")
        with timeit("Save the merged picture in {}".format(self.app.previous_picture_file)):
            self.app.previous_picture.save(self.app.previous_picture_file)

    def validate_transition(self, events):
        if self.app.printer.is_installed() and self.app.config.getfloat('PRINTER', 'printer_delay') > 0:
            return 'print'
        else:
            return 'finish'  # Can not print


class StatePrint(State):

    def __init__(self):
        State.__init__(self, 'print')
        self.timer = PoolingTimer(self.app.config.getfloat('PRINTER', 'printer_delay'))
        self.printed = False

    def entry_actions(self):
        self.printed = False
        with timeit("Display the merged picture"):
            self.app.window.set_print_number(len(self.app.printer.get_all_tasks()))
            self.app.window.show_print(self.app.previous_picture)
        self.app.led_print.blink()
        # Reset timeout in case of settings changed
        self.timer.timeout = self.app.config.getfloat('PRINTER', 'printer_delay')
        self.timer.start()

    def do_actions(self, events):
        if self.app.find_print_event(events) and self.app.previous_picture_file:

            with timeit("Send final picture to printer"):
                self.app.led_print.switch_on()
                self.app.printer.print_file(self.app.previous_picture_file,
                                            self.app.config.getint('PRINTER', 'nbr_copies'))

            time.sleep(1)  # Just to let the LED switched on
            self.app.nbr_printed += 1
            self.app.led_print.blink()
            self.printed = True

    def validate_transition(self, events):
        if self.timer.is_timeout() or self.printed:
            if self.printed:
                self.app.window.set_print_number(len(self.app.printer.get_all_tasks()))
            return 'finish'


class StateFinish(State):

    def __init__(self, timeout):
        State.__init__(self, 'finish')
        self.timer = PoolingTimer(timeout)

    def entry_actions(self):
        self.app.window.show_finished()
        self.timer.start()

    def validate_transition(self, events):
        if self.timer.is_timeout():
            return 'wait'


class PiApplication(object):

    def __init__(self, config):
        self.config = config

        # Clean directory where pictures are saved
        self.savedir = config.getpath('GENERAL', 'directory')
        if not osp.isdir(self.savedir):
            os.makedirs(self.savedir)
        if osp.isdir(self.savedir) and config.getboolean('GENERAL', 'clear_on_startup'):
            shutil.rmtree(self.savedir)
            os.makedirs(self.savedir)

        # Prepare GPIO, physical pins mode
        GPIO.setmode(GPIO.BOARD)

        # Prepare the pygame module for use
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        pygame.init()
        # Dont catch mouse motion to avoid filling the queue during long actions
        pygame.event.set_blocked(pygame.MOUSEMOTION)

        # Create window of (width, height)
        init_size = self.config.gettyped('WINDOW', 'size')
        if not isinstance(init_size, str):
            self.window = PtbWindow('Pibooth', init_size)
        else:
            self.window = PtbWindow('Pibooth')

        self.state_machine = StateMachine(self)
        self.state_machine.add_state(StateWait())
        self.state_machine.add_state(StateChoose(30))  # 30s before going back to the start
        self.state_machine.add_state(StateChosen(4))
        self.state_machine.add_state(StateCapture())
        self.state_machine.add_state(StateProcessing())
        self.state_machine.add_state(StatePrint())
        self.state_machine.add_state(StateFinish(0.5))

        # Initialize the camera
        if camera.gp_camera_connected() and camera.rpi_camera_connected():
            cam_class = camera.HybridCamera
        elif camera.gp_camera_connected():
            cam_class = camera.GpCamera
        elif camera.rpi_camera_connected():
            cam_class = camera.RpiCamera
        else:
            raise EnvironmentError("Neither PiCamera nor GPhoto2 camera detected")

        self.camera = cam_class(config.getint('CAMERA', 'iso'),
                                config.gettyped('CAMERA', 'resolution'),
                                config.getint('CAMERA', 'rotation'),
                                config.getboolean('CAMERA', 'flip'))

        # Initialize the hardware buttons
        self.led_picture = PtbLed(config.getint('CONTROLS', 'picture_led_pin'))
        self.button_picture = PtbButton(config.getint('CONTROLS', 'picture_btn_pin'),
                                        config.getfloat('CONTROLS', 'debounce_delay'))

        self.led_print = PtbLed(config.getint('CONTROLS', 'print_led_pin'))
        self.button_print = PtbButton(config.getint('CONTROLS', 'print_btn_pin'),
                                      config.getfloat('CONTROLS', 'debounce_delay'))

        self.led_startup = PtbLed(config.getint('CONTROLS', 'startup_led_pin'))
        self.led_preview = PtbLed(config.getint('CONTROLS', 'preview_led_pin'))

        # Initialize the printer
        self.printer = PtbPrinter(config.get('PRINTER', 'printer_name'))

        # Variables shared between states
        self.dirname = None
        self.nbr_captures = None
        self.capture_choices = (4, 1)
        self.nbr_printed = 0
        self.previous_picture = None
        self.previous_picture_file = None

    def initialize(self):
        """Restore the application with initial parameters defined in the
        configuration file.
        Only parameters that can be changed at runtime are restored.
        """
        # Handle the language configuration, save it as a class attribute for easy access
        language = self.config.get('GENERAL', 'language')
        if language not in get_supported_languages():
            LOGGER.warning("Unsupported language '%s', fallback to English", language)
        else:
            PiConfigParser.language = language

        # Set the captures choices
        choices = self.config.gettyped('PICTURE', 'captures')
        if isinstance(choices, int):
            choices = (choices,)
        for chx in choices:
            if chx not in [1, 2, 3, 4]:
                LOGGER.warning("Invalid captures number '%s' in config, fallback to '%s'",
                               chx, self.capture_choices)
                choices = self.capture_choices
                break
        self.capture_choices = choices

        # Handle autostart of the application
        self.config.enable_autostart(self.config.getboolean('GENERAL', 'autostart'))

        self.window.arrow_location = self.config.get('WINDOW', 'arrows')
        self.window.arrow_offset = self.config.getint('WINDOW', 'arrows_x_offset')
        self.window.drop_cache()

        # Handle window size
        size = self.config.gettyped('WINDOW', 'size')
        if isinstance(size, str) and size.lower() == 'fullscreen':
            if not self.window.is_fullscreen:
                self.window.toggle_fullscreen()
        else:
            if self.window.is_fullscreen:
                self.window.toggle_fullscreen()

        # Initialize state machine
        if self.config.getboolean('GENERAL', 'failsafe'):
            self.state_machine.add_failsafe_state(StateFailSafe(2))
        else:
            self.state_machine.remove_state('failsafe')
        self.state_machine.set_state('wait')

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
        event_picture = None
        event_print = None
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE and\
                    (type_filter is None or type_filter == event.type):
                return event
            if event.type == BUTTON_DOWN:
                if event.pin == self.button_picture and (type_filter is None or type_filter == event.type):
                    event_picture = event
                elif event.pin == self.button_print and (type_filter is None or type_filter == event.type):
                    event_print = event
            if event_picture and event_print:
                return event_picture  # One of both (return != None is enough)

        return None

    def find_fullscreen_event(self, events):
        """Return the first found event if found in the list.
        """
        for event in events:
            if  event.type == pygame.KEYDOWN and\
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

    def find_picture_event(self, events, type_filter=None):
        """Return the first found event if found in the list.
        """
        for event in events:
            if (event.type == pygame.KEYDOWN and event.key == pygame.K_p) or \
                    (event.type == BUTTON_DOWN and event.pin == self.button_picture):
                if type_filter is None or type_filter == event.type:
                    return event
            elif event.type == pygame.MOUSEBUTTONUP:
                rect = self.window.get_rect()
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
                rect = self.window.get_rect()
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
                    (event.type == BUTTON_DOWN and event.pin == self.button_picture):
                event.key = pygame.K_LEFT
                return event
            elif (event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT) or \
                    (event.type == BUTTON_DOWN and event.pin == self.button_print):
                event.key = pygame.K_RIGHT
                return event
            elif event.type == pygame.MOUSEBUTTONUP:
                rect = self.window.get_rect()
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
            self.led_startup.switch_on()
            self.initialize()
            menu = None
            fps = 40

            while True:
                events = list(pygame.event.get())

                if self.find_quit_event(events):
                    break

                if self.find_fullscreen_event(events):
                    self.window.toggle_fullscreen()

                event = self.find_resize_event(events)
                if event:
                    self.window.resize(event.size)

                if not menu and self.find_settings_event(events):
                    menu = PiConfigMenu(self.window, self.config, fps)
                    menu.show()

                if menu and menu.is_shown():
                    # Convert HW button events to keyboard events for menu
                    if self.find_settings_event(events, BUTTON_DOWN):
                        events.insert(0, menu.create_back_event())
                    if self.find_picture_event(events, BUTTON_DOWN):
                        events.insert(0, menu.create_next_event())
                    elif self.find_print_event(events, BUTTON_DOWN):
                        events.insert(0, menu.create_click_event())

                    menu.process(events)
                elif menu and not menu.is_shown():
                    self.initialize()
                    menu = None
                else:
                    self.state_machine.process(events)

                pygame.display.update()
                clock.tick(fps)  # Ensure the program will never run at more than x frames per second

        finally:
            self.led_startup.quit()
            self.led_preview.quit()
            self.led_picture.quit()
            self.led_print.quit()
            GPIO.cleanup()
            self.camera.quit()
            self.printer.quit()
            pygame.quit()


def main():
    """Application entry point.
    """
    parser = argparse.ArgumentParser(usage="%(prog)s [options]", description=pibooth.__doc__)

    parser.add_argument('--version', action='version', version=pibooth.__version__,
                        help=u"show program's version number and exit")

    parser.add_argument("--config", action='store_true',
                        help=u"edit the current configuration")

    parser.add_argument("--reset", action='store_true',
                        help=u"restore the default configuration")

    parser.add_argument("--fonts", action='store_true',
                        help=u"display all available fonts")

    parser.add_argument("--log", default=None,
                        help=u"save console output to the given file")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("-v", "--verbose", dest='logging', action='store_const', const=logging.DEBUG,
                       help=u"report more information about operations", default=logging.INFO)
    group.add_argument("-q", "--quiet", dest='logging', action='store_const', const=logging.WARNING,
                       help=u"report only errors and warnings", default=logging.INFO)

    options, _args = parser.parse_known_args()

    configure_logging(options.logging, '[ %(levelname)-8s] %(name)-18s: %(message)s', filename=options.log)

    config = PiConfigParser("~/.config/pibooth/pibooth.cfg", options.reset)

    if options.config:
        LOGGER.info("Editing the photo booth configuration...")
        config.open_editor()
        config.enable_autostart(config.getboolean('GENERAL', 'autostart'))
    elif options.fonts:
        print_columns_words(get_available_fonts(), 3)
    elif not options.reset:
        LOGGER.info("Starting the photo booth application...")
        app = PiApplication(config)
        app.main_loop()


if __name__ == '__main__':
    main()
