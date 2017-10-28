#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Photo booth main module.
"""

import os
import ast
import time
import shutil
import pygame
import os.path as osp
from RPi import GPIO
try:
    import configparser
except ImportError:
    # Python 2.x fallback
    import ConfigParser as configparser
from pibooth.window import PtbWindow
from pibooth.controls.camera import PtbCamera
from pibooth.pictures.concatenate_images import generate_photo_from_files
from pibooth.controls.light import PtbLed


class PtbConfigParser(configparser.ConfigParser):

    """Enhenced configuration file parser.
    """

    def __init__(self, filename):
        configparser.ConfigParser.__init__(self)
        if not osp.isfile(filename):
            raise ValueError("No sush configuration file: '%s'" % filename)
        self.filename = filename
        self.read(filename)

    def get(self, section, option, default=None, **kwargs):
        """
        Override the default function of ConfigParser to add a
        default value if section or option is not found.

        :param default: default value if section or option is not found
        :type default: str
        """
        if self.has_section(section) and self.has_option(section, option):
            value = configparser.ConfigParser.get(self, section, option, **kwargs)
            return value
        return default

    def gettyped(self, section, option, default=None):
        """
        Get a value from config and try to convert it in a native Python
        type (using the :py:mod:`ast` module).

        :param default: default value if section or option is not found
        :type default: str
        """
        value = self.get(section, option, default)
        try:
            return ast.literal_eval(value)
        except (ValueError, SyntaxError):
            return value


class PtbApplication(object):

    def __init__(self, config, savedir):
        self.config = config
        self.savedir = savedir

        # Prepare GPIO, physical pins mode
        GPIO.setmode(GPIO.BOARD)

        # Prepare the pygame module for use
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        pygame.init()

        # Create window of (width, height)
        self.window = PtbWindow((self.config.getint('WINDOW', 'width'),
                                 self.config.getint('WINDOW', 'height')))

        # Initialize the camera
        self.camera = PtbCamera((self.window.width, self.window.height),
                                config.getint('CAMERA', 'camera_iso'),
                                config.getboolean('CAMERA', 'high_resolution'))

        # Setup the LED on pin 7 (BOARD number)
        self.led = PtbLed(7)

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
        P pressed.
        """
        return event.type == pygame.KEYDOWN and event.key == pygame.K_p

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

                if not self.is_picture_event(event) and not captures:
                    self.window.show_intro()
                else:
                    if not captures:
                        # Start a new capture sequence
                        self.window.show_instructions()
                        print("Start new pictures sequence")
                        dirname = self.create_new_directory()
                        time.sleep(1)

                    self.led.blink()
                    if self.config.getboolean('WINDOW', 'capture_counter'):
                        self.window.show_counter(not captures)
                        time.sleep(0.5)

                    self.camera.preview()
                    time.sleep(self.config.getint('CAMERA', 'preview_delay'))
                    self.window.clear()
                    image_file_name = osp.join(dirname, "ptb{:03}.jpg".format(len(captures)))
                    self.led.switch_on()
                    self.camera.capture(image_file_name)
                    print("Picture saved in {}".format(image_file_name))
                    captures.append(image_file_name)

                if len(captures) >= self.config.getint('CAMERA', 'captures'):
                    self.window.show_wait()
                    self.led.switch_off()
                    print("Creating merged image")
                    merged_file = osp.join(dirname, "ptb_merged.jpg")
                    footer_texts = [self.config.get('GENERAL', 'footer_text1', ''),
                                    self.config.get('GENERAL', 'footer_text2', '')]
                    bg_color = self.config.gettyped('GENERAL', 'bg_color', (255, 255, 255))
                    text_color = self.config.gettyped('GENERAL', 'text_color', (0, 0, 0))
                    generate_photo_from_files(captures, merged_file, footer_texts,
                                              bg_color, text_color)

                    print("Display the picture")
                    self.window.show_image_from_file(merged_file)
                    time.sleep(5)
                    # Finish the sequence
                    self.window.show_finished()
                    time.sleep(1)
                    captures = []

        finally:
            GPIO.cleanup()
            self.camera.quit()
            pygame.quit()


def main():
    """Application entry point.
    """
    config = PtbConfigParser(osp.join(osp.dirname(osp.abspath(__file__)), "config.ini"))

    savedir = osp.expanduser(config.get('GENERAL', 'directory', '~'))
    if not osp.isdir(savedir):
        os.makedirs(savedir)
    if osp.isdir(savedir) and config.getboolean('GENERAL', 'clear_on_startup'):
        shutil.rmtree(savedir)
        os.makedirs(savedir)

    app = PtbApplication(config, savedir)
    print("Starting Photo Booth application...")
    app.main_loop()


if __name__ == '__main__':
    main()
