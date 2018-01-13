# -*- coding: utf-8 -*-

import os
import time
import pygame
from pibooth import pictures
from PIL import Image


class PtbWindow(object):

    """Manage the window.
    """

    def __init__(self, size):
        self.__size = size

        # Save the desktop mode, shall be done before `setmode` (SDL 1.2.10, and pygame 1.8.0)
        info = pygame.display.Info()

        pygame.display.set_caption('Pibooth')
        self.surface = pygame.display.set_mode(size, pygame.RESIZABLE)
        self.display_size = (info.current_w, info.current_h)
        self.is_fullscreen = False

        self._current_frame = None

    def _centered_pos(self, image):
        """
        Return the position of the given image to be centered on window.
        """
        return image.get_rect(center=self.surface.get_rect().center)

    def _show_and_memorize(self, image_name):
        """Show image and memorize it. If the image is the same as the
        current displayed, nothing is done.
        """
        if self._current_frame != image_name:
            image = pictures.get_image(image_name, self.size)
            self.clear()
            self.surface.blit(image, self._centered_pos(image))
            pygame.display.update()
            self._current_frame = image_name

    def get_rect(self):
        """Return a Rect object as defined in pygame. The position
        represent the absolute position considering the window
        centered on screen.
        """
        return self.surface.get_rect(center=(self.display_size[0] / 2, self.display_size[1] / 2))

    @property
    def size(self):
        """Return the current window size.
        """
        if self.is_fullscreen:
            return self.display_size
        else:
            return self.__size

    def resize(self, size):
        """Resize the window keeping aspect ratio.
        """
        self.__size = size
        self.surface = pygame.display.set_mode(self.size, pygame.RESIZABLE)
        if self._current_frame:
            image = pictures.get_image(self._current_frame, self.size)
            self.surface.blit(image, self._centered_pos(image))
            pygame.display.update()

    def show_intro(self):
        """Show introduction view.
        """
        self._show_and_memorize("intro.png")

    def show_countdown(self, timeout):
        """Show a countdown of `timeout` seconds.
        """
        timeout = int(timeout)
        if timeout < 1:
            raise ValueError("Start time shall be greater than 0")

        font = pygame.font.SysFont('Consolas', 400)
        while timeout > 0:
            self.clear()
            image = font.render(str(timeout), True, (255, 255, 255))
            self.surface.blit(image, self._centered_pos(image))
            pygame.display.update()
            time.sleep(1)
            timeout -= 1

    def show_wait(self):
        """Show wait view.
        """
        self._show_and_memorize("processing.png")

    def show_finished(self):
        """Show finished view.
        """
        self._show_and_memorize("finished.png")

    def show_pil_image(self, image):
        """Show a PIL image.
        """
        image = image.resize(pictures.resize_keep_aspect_ratio(image.size, self.size), Image.ANTIALIAS)
        image = pygame.image.fromstring(image.tobytes(), image.size, image.mode)

        self.clear()
        self.surface.blit(image, self._centered_pos(image))
        pygame.display.update()
        self._current_frame = None

    def show_file_image(self, image_file):
        """
        Show the merged file
        """
        self._show_and_memorize(os.path.abspath(image_file))

    def flash(self, count):
        """Flash the window content.
        """
        for _ in range(count):
            self.surface.fill((255, 255, 255))
            pygame.display.update()
            time.sleep(0.01)
            self.clear()
            time.sleep(0.01)

    def clear(self):
        """Clear the window content.
        """
        self.surface.fill((0, 0, 0))
        pygame.display.update()
        self._current_frame = None

    def toggle_fullscreen(self):
        """Set window to full screen.
        """
        if self.is_fullscreen:
            self.is_fullscreen = False  # Set before get size
            self.surface = pygame.display.set_mode(self.size, pygame.RESIZABLE)
        else:
            self.is_fullscreen = True  # Set before get size
            self.surface = pygame.display.set_mode(self.size, pygame.FULLSCREEN)

        if self._current_frame:
            image = pictures.get_image(self._current_frame, self.size)
            self.surface.blit(image, self._centered_pos(image))
            pygame.display.update()
