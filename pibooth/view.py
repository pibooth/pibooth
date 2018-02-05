# -*- coding: utf-8 -*-

import time
import pygame
from pygame import gfxdraw
from pibooth import pictures, fonts
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

        self._current_background = None
        self._current_foreground = None
        self._picture_number = (0, 4)  # current / max

    def _clear(self):
        """Clear the window content.
        """
        self.surface.fill((0, 0, 0))
        self._current_background = None
        self._current_foreground = None

    def _show_and_memorize(self, image_name, update=True):
        """Show image and memorize it. If the image is the same as the
        current displayed, nothing is done.
        """
        if self._current_background != image_name:
            image = pictures.get_image(image_name, self.size)
            self._clear()
            self.surface.blit(image, self._centered_pos(image))
            self._current_background = image_name
            self._update_picture_number()
            if update:
                pygame.display.update()

    def _update_picture_number(self):
        """Update the pictures counter displayed.
        """
        if self._picture_number[0] == 0:
            return  # Dont show cunter: no picture taken
        center = self.surface.get_rect().center
        radius = 10
        border = 20
        color = (255, 255, 255)
        x = center[0] - (2 * radius * self._picture_number[1] + border * (self._picture_number[1] - 1)) // 2
        y = self.size[1] - radius - border
        for nbr in range(self._picture_number[1]):
            gfxdraw.aacircle(self.surface, x, y, radius, color)
            if self._picture_number[0] > nbr:
                gfxdraw.aacircle(self.surface, x, y, radius - 3, color)  # Because anti-aliased filled circle doesn't exist
                gfxdraw.filled_circle(self.surface, x, y, radius - 3, color)
            x += (2 * radius + border)

    def _centered_pos(self, image):
        """
        Return the position of the given image to be centered on window.
        """
        return image.get_rect(center=self.surface.get_rect().center)

    def _left_pos(self, image):
        """
        Return the position of the given image to be put on the left of the screen
        """
        return image.get_rect(center=(self.surface.get_rect().centerx // 2, self.surface.get_rect().centery))

    def _right_pos(self, image):
        """
        Return the position of the given image to be put on the right of the screen
        """
        return image.get_rect(center=(self.surface.get_rect().centerx + self.surface.get_rect().centerx // 2, self.surface.get_rect().centery))

    @property
    def size(self):
        """Return the current window size.
        """
        if self.is_fullscreen:
            return self.display_size
        else:
            return self.__size

    def get_rect(self):
        """Return a Rect object (as defined in pygame) for this window. The position represent
        the absolute position considering the window centered on screen.
        """
        return self.surface.get_rect(center=(self.display_size[0] / 2, self.display_size[1] / 2))

    def resize(self, size):
        """Resize the window keeping aspect ratio.
        """
        self.__size = size
        self.surface = pygame.display.set_mode(self.size, pygame.RESIZABLE)
        if self._current_background:
            image = pictures.get_image(self._current_background, self.size)
            self.surface.blit(image, self._centered_pos(image))
        self._update_picture_number()
        pygame.display.update()

    def show_intro(self, image=None):
        """Show introduction view.
        """
        self._show_and_memorize("intro.png", image is None)
        if image and image != self._current_foreground:
            image = image.resize(pictures.resize_keep_aspect_ratio(image.size, self.size), Image.ANTIALIAS)
            image = pygame.image.fromstring(image.tobytes(), image.size, image.mode)
            self.surface.blit(image, self._right_pos(image))
            pygame.display.update()
        self._current_foreground = image

    def show_choice(self, number):
        """Show the choice view.
        """
        self._show_and_memorize("choice{}.png".format(number))

    def show_countdown(self, timeout):
        """Show a countdown of `timeout` seconds. Returns when the countdown
        is finished.
        """
        timeout = int(timeout)
        if timeout < 1:
            raise ValueError("Start time shall be greater than 0")

        font = pygame.font.Font(fonts.get_filename("Amatic-Bold.ttf"), self.size[1] - 150)
        while timeout > 0:
            self._clear()
            image = font.render(str(timeout), True, (255, 255, 255))
            pos = self._centered_pos(image)
            self.surface.blit(image, (pos[0], pos[1] - 60))  # Margin due to picture counter position
            self._update_picture_number()
            pygame.display.update()
            time.sleep(1)
            timeout -= 1

    def show_wait(self):
        """Show wait view.
        """
        self._picture_number = (0, self._picture_number[1])
        self._show_and_memorize("processing.png")

    def show_print(self, image=None):
        """Show print view.
        """
        self._picture_number = (0, self._picture_number[1])
        self._show_and_memorize("print.png", image is None)
        if image and image != self._current_foreground:
            image = image.resize(pictures.resize_keep_aspect_ratio(image.size, self.size), Image.ANTIALIAS)
            image = pygame.image.fromstring(image.tobytes(), image.size, image.mode)
            self.surface.blit(image, self._left_pos(image))
            pygame.display.update()
        self._current_foreground = image

    def show_finished(self):
        """Show finished view.
        """
        self._picture_number = (0, self._picture_number[1])
        self._show_and_memorize("finished.png")

    def flash(self, count):
        """Flash the window content.
        """
        for _ in range(count):
            self.surface.fill((255, 255, 255))
            pygame.display.update()
            time.sleep(0.01)
            self._clear()
            time.sleep(0.01)
        self._update_picture_number()
        pygame.display.update()

    def set_picture_number(self, current_nbr, total_nbr):
        """Set the current number of pictures taken.
        """
        if total_nbr < 1:
            raise ValueError("Total number of captures shall be greater than 0")

        self._clear()
        self._picture_number = (current_nbr, total_nbr)
        self._update_picture_number()
        pygame.display.update()

    def toggle_fullscreen(self):
        """Set window to full screen.
        """
        if self.is_fullscreen:
            self.is_fullscreen = False  # Set before get size
            self.surface = pygame.display.set_mode(self.size, pygame.RESIZABLE)
        else:
            self.is_fullscreen = True  # Set before get size
            self.surface = pygame.display.set_mode(self.size, pygame.FULLSCREEN)

        if self._current_background:
            image = pictures.get_image(self._current_background, self.size)
            self.surface.blit(image, self._centered_pos(image))

        self._update_picture_number()
        pygame.display.update()
