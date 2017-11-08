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
from pibooth.window import PtbWindow
from pibooth.config import PtbConfigParser, edit_configuration
from pibooth.controls import camera
from pibooth.pictures.concatenate_images import generate_photo_from_files
from pibooth.controls.light import PtbLed
from pibooth.controls.button import BUTTON_DOWN, PtbButton


class PtbApplication(object):

    def __init__(self, config):
        self.config = config

        # Clean directory where pictures are saved
        savedir = osp.expanduser(config.get('GENERAL', 'directory'))
        if not osp.isdir(savedir):
            os.makedirs(savedir)
        if osp.isdir(savedir) and config.getboolean('GENERAL', 'clear_on_startup'):
            shutil.rmtree(savedir)
            os.makedirs(savedir)
        self.savedir = savedir

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
        self.camera = camera.get_camera(config.gettyped('WINDOW', 'preview_offset'),
                                        config.getint('CAMERA', 'iso'),
                                        config.gettyped('CAMERA', 'resolution'))

        self.led = PtbLed(7)
        self.button_print = PtbButton(13, config.getfloat('GENERAL', 'debounce_delay'))
        self.button_picture = PtbButton(11, config.getfloat('GENERAL', 'debounce_delay'))

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
            while True:
                event = pygame.event.poll()    # Take one event

                if self.is_quit_event(event):
                    break

                if self.is_fullscreen_event(event):
                    self.window.toggle_fullscreen()

                if self.is_resize_event(event):
                    self.window.resize(event.size)

                if not self.is_picture_event(event) and not captures:
                    self.window.show_intro()
                else:
                    self.led.blink()
                    if not captures:
                        print("Start new pictures sequence")
                        self.window.show_instructions()
                        dirname = self.create_new_directory()
                        time.sleep(1)

                    if self.config.getboolean('WINDOW', 'capture_counter'):
                        self.window.show_counter(not captures)
                        time.sleep(0.5)

                    self.camera.preview(self.window.get_rect())
                    time.sleep(self.config.getint('WINDOW', 'preview_delay'))

                    image_file_name = osp.join(dirname, "ptb{:03}.jpg".format(len(captures)))
                    self.led.switch_on()
                    self.window.flash(2)
                    self.camera.capture(image_file_name)
                    print("Picture saved in {}".format(image_file_name))
                    captures.append(image_file_name)

                if len(captures) >= self.config.getint('PICTURE', 'captures'):
                    self.window.show_wait()
                    self.led.switch_off()
                    print("Creating merged image")
                    merged_file = osp.join(dirname, "ptb_merged.jpg")
                    footer_texts = [self.config.get('PICTURE', 'footer_text1'),
                                    self.config.get('PICTURE', 'footer_text2')]
                    bg_color = self.config.gettyped('PICTURE', 'bg_color')
                    text_color = self.config.gettyped('PICTURE', 'text_color')
                    generate_photo_from_files(captures, merged_file, footer_texts,
                                              bg_color, text_color)

                    print("Display the picture")
                    self.window.clear()
                    self.window.show_image_from_file(merged_file)
                    time.sleep(5)
                    # Finish the sequence
                    self.window.clear()
                    self.window.show_finished()
                    time.sleep(1)
                    captures = []

                if self.is_print_event(event):
                    print("Send pictures to printer")

        finally:
            GPIO.cleanup()
            self.camera.quit()
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
    else:
        print("Starting the Photo Booth application...")
        app = PtbApplication(config)
        app.main_loop()


if __name__ == '__main__':
    main()
