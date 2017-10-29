#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Photobooth main module.
"""

import os
import time
import shutil
import pygame
import os.path as osp
from RPi import GPIO
from pibooth.window import PtbWindow
from pibooth.config import PtbConfigParser
from pibooth.controls.camera import PtbCamera
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

        # Create window of (width, height)
        self.window = PtbWindow((self.config.getint('WINDOW', 'width'),
                                 self.config.getint('WINDOW', 'height')))

        # Initialize the camera
        self.camera = PtbCamera((self.window.width, self.window.height),
                                config.getint('CAMERA', 'camera_iso'),
                                config.getboolean('CAMERA', 'high_resolution'))

        self.led = PtbLed(7)
        self.button_picture = PtbButton(11, config.getint('GENERAL', 'debounce_delay'))
        self.button_print = PtbButton(13, config.getint('GENERAL', 'debounce_delay'))

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
                    footer_texts = [self.config.get('MERGED', 'footer_text1'),
                                    self.config.get('MERGED', 'footer_text2')]
                    bg_color = self.config.gettyped('MERGED', 'bg_color')
                    text_color = self.config.gettyped('MERGED', 'text_color')
                    generate_photo_from_files(captures, merged_file, footer_texts,
                                              bg_color, text_color)

                    print("Display the picture")
                    self.window.show_image_from_file(merged_file)
                    time.sleep(5)
                    # Finish the sequence
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
    config = PtbConfigParser("~/.config/pibooth/pibooth.cfg")

    app = PtbApplication(config)

    print("Starting Photo Booth application...")
    app.main_loop()


if __name__ == '__main__':
    main()
