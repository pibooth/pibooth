#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Photobooth main module.
"""

import os
import time
import shutil
import logging
import pygame
import argparse
import os.path as osp
from RPi import GPIO
import pibooth
from pibooth.utils import timeit, PoolingTimer
from pibooth.window import PtbWindow
from pibooth.config import PtbConfigParser, edit_configuration
from pibooth.controls import camera
from pibooth.pictures.concatenate import generate_picture_from_files
from pibooth.controls.light import PtbLed
from pibooth.controls.button import BUTTON_DOWN, PtbButton
from pibooth.controls.printer import PtbPrinter


class PtbApplication(object):

    def __init__(self, config):
        self.config = config

        # Clean directory where pictures are saved
        self.savedir = osp.expanduser(config.get('GENERAL', 'directory'))
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
        self.window = PtbWindow(config.gettyped('WINDOW', 'size'))

        # Initialize the camera
        if camera.rpi_camera_connected():
            cam_class = camera.RpiCamera
        elif camera.gp_camera_commected():
            cam_class = camera.GpCamera
        else:
            raise EnvironmentError("Neither Pi Camera nor GPhoto2 camera detected")

        self.camera = cam_class(config.getint('CAMERA', 'iso'),
                                config.gettyped('CAMERA', 'resolution'))

        self.led_picture = PtbLed(7)
        self.button_picture = PtbButton(11, config.getfloat('GENERAL', 'debounce_delay'))

        self.led_print = PtbLed(15)
        self.button_print = PtbButton(13, config.getfloat('GENERAL', 'debounce_delay'))

        self.printer = PtbPrinter()

    def create_new_directory(self):
        """Create a new directory to save pictures.
        """
        name = osp.join(self.savedir, time.strftime("%Y-%m-%d-%H-%M-%S"))
        os.makedirs(name)
        return name

    def is_quit_event(self, event):
        """Return True if the application have to quite.
        Close button clicked or ESC pressed.
        """
        return event.type == pygame.QUIT or\
            (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE)

    def is_fullscreen_event(self, event):
        """Return True if the application have to toogle fullscreen.
        CTRL + F pressed.
        """
        return event.type == pygame.KEYDOWN and\
            event.key == pygame.K_f and pygame.key.get_mods() & pygame.KMOD_CTRL

    def is_picture_event(self, event):
        """Return True if the application have to take the photo.
        P or physical button pressed.
        """
        return (event.type == pygame.KEYDOWN and event.key == pygame.K_p) or \
            (event.type == BUTTON_DOWN and event.pin == self.button_picture)

    def is_print_event(self, event):
        """Return True if the application have to print the photo.
        Ctrl + E or physical button pressed.
        """
        return (event.type == pygame.KEYDOWN and event.key == pygame.K_e and
                pygame.key.get_mods() & pygame.KMOD_CTRL) or \
            (event.type == BUTTON_DOWN and event.pin == self.button_print)

    def is_resize_event(self, event):
        """Return True if the window has been resized. This method ensure
        to only process the last resize event (avoid refresh lag).
        """
        return event.type == pygame.VIDEORESIZE and not pygame.event.peek(pygame.VIDEORESIZE)

    def main_loop(self):
        """Run the main game loop.
        """
        try:
            captures = []
            last_merged_picture = None
            printing_timer = None
            while True:
                event = pygame.event.poll()    # Take one event

                if self.is_quit_event(event):
                    break

                if self.is_fullscreen_event(event):
                    self.window.toggle_fullscreen()

                if self.is_resize_event(event):
                    self.window.resize(event.size)

                if not self.is_picture_event(event) and not captures and not printing_timer:
                    self.window.show_intro()
                elif not printing_timer:
                    self.led_print.switch_off()
                    self.led_picture.blink()
                    if not captures:
                        print("Start new pictures sequence")
                        last_merged_picture = None  # Print button will do nothing
                        dirname = self.create_new_directory()
                        self.camera.preview(self.window.get_rect())

                    self.window.set_picture_number(len(captures) + 1, self.config.getint('PICTURE', 'captures'))

                    if self.config.getboolean('WINDOW', 'preview_countdown'):
                        self.window.show_countdown(self.config.getint('WINDOW', 'preview_delay'))
                    else:
                        time.sleep(self.config.getint('WINDOW', 'preview_delay'))

                    self.led_picture.switch_on()
                    if self.config.getboolean('WINDOW', 'flash'):
                        self.window.flash(2)

                    image_file_name = osp.join(dirname, "ptb{:03}.jpg".format(len(captures)))
                    with timeit("Take picture and save it in {}".format(image_file_name)):
                        self.camera.capture(image_file_name)
                        captures.append(image_file_name)

                if len(captures) >= self.config.getint('PICTURE', 'captures'):
                    self.camera.stop_preview()
                    self.window.show_wait()
                    self.led_picture.switch_off()

                    with timeit("Creating merged picture"):
                        footer_texts = [self.config.get('PICTURE', 'footer_text1'),
                                        self.config.get('PICTURE', 'footer_text2')]
                        bg_color = self.config.gettyped('PICTURE', 'bg_color')
                        text_color = self.config.gettyped('PICTURE', 'text_color')
                        picture = generate_picture_from_files(captures, footer_texts, bg_color, text_color)

                    last_merged_picture = osp.join(dirname, "ptb_merged.jpg")
                    with timeit("Save the merged picture in {}".format(last_merged_picture)):
                        picture.save(last_merged_picture)

                    with timeit("Display the merged picture"):
                        self.window.show_pil_image(picture)

                    printing_timer = PoolingTimer(5)
                    self.led_print.switch_on()
                    captures = []

                if self.is_print_event(event) and last_merged_picture:
                    print("Send pictures to printer")
                    self.led_print.blink()
                    self.printer.print_file(last_merged_picture)
                    time.sleep(0.5)
                    self.led_print.switch_on()

                if printing_timer and printing_timer.is_timeout():
                    # Finish the sequence
                    self.window.show_finished()
                    time.sleep(0.5)
                    printing_timer = None

        finally:
            self.led_picture.switch_off()
            self.led_print.switch_off()
            GPIO.cleanup()
            self.camera.quit()
            self.printer.quit()
            pygame.quit()


def main():
    """Application entry point.
    """
    parser = argparse.ArgumentParser(usage="%(prog)s [options]", description=pibooth.__doc__)

    parser.add_argument('-v', '--version', action='version', version=pibooth.__version__,
                        help=u"show program's version number and exit")

    parser.add_argument("--config", action='store_true',
                        help=u"edit the current configuration")

    parser.add_argument("--reset", action='store_true',
                        help=u"restore the default configuration")

    logging.basicConfig(format='%(levelname)s: %(name)s: %(message)s', level=logging.WARNING)

    options, _args = parser.parse_known_args()

    config = PtbConfigParser("~/.config/pibooth/pibooth.cfg", options.reset)

    if options.config:
        print("Editing the Photo Booth configuration...")
        edit_configuration(config)
    elif not options.reset:
        print("Starting the Photo Booth application...")
        app = PtbApplication(config)
        app.main_loop()


if __name__ == '__main__':
    main()
