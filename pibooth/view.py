# -*- coding: utf-8 -*-

import time
import pygame
from pygame import gfxdraw
from pibooth import pictures
from PIL import Image


class PtbWindow(object):

    """Manage the window.
    """

    def __init__(self, title, size, use_buffer):
        if isinstance(size, str) and size.lower() == 'fullscreen':
            self.__size = (800, 480)
        elif isinstance(size, (tuple, list)):
            self.__size = size
        else:
            raise TypeError("Invalid size '{}' ({})".format(size, type(size)))

        # Save the desktop mode, shall be done before `setmode` (SDL 1.2.10, and pygame 1.8.0)
        info = pygame.display.Info()

        pygame.display.set_caption(title)
        self.is_fullscreen = False
        self.use_buffer = use_buffer
        self.display_size = (info.current_w, info.current_h)
        self.surface = pygame.display.set_mode(self.__size, pygame.RESIZABLE)

        self._buffered_images = {}
        self._current_background = None
        self._current_foreground = None
        self._picture_number = (0, 4)  # (current, max)

        self._pos_map = {'center': self._centered_pos,
                         'right': self._right_pos,
                         'left': self._left_pos}

        if isinstance(size, str) and size.lower() == 'fullscreen':
            self.toggle_fullscreen()

    def _clear(self):
        """Clear the window content.
        """
        self.surface.fill((0, 0, 0))

    def _update_foreground(self, pil_image, pos='center'):
        """Show a PIL image on the foreground.
        """
        image_name = id(pil_image)
        if pil_image:
            buff_size, buff_image = self._buffered_images.get(image_name, (None, None))
            if buff_image and self.size == buff_size:
                image = buff_image
            else:
                pil_image = pil_image.resize(pictures.resize_keep_aspect_ratio(pil_image.size, self.size), Image.ANTIALIAS)
                image = pygame.image.fromstring(pil_image.tobytes(), pil_image.size, pil_image.mode)
                if self.use_buffer:
                    self._buffered_images.pop(self._current_foreground, None)
                    self._buffered_images[image_name] = (self.size, image)
                self._current_foreground = image_name

            self.surface.blit(image, self._pos_map[pos](image))

    def _update_background(self, image_name):
        """Show image on the background.
        """
        buff_size, buff_image = self._buffered_images.get(image_name, (None, None))
        if buff_image and self.size == buff_size:
            image = buff_image
        else:
            image = pictures.get_image(image_name, self.size)
        self._clear()
        self.surface.blit(image, self._centered_pos(image))
        self._update_picture_number()
        if self.use_buffer and self.size != buff_size:
            self._buffered_images[image_name] = (self.size, image)
        self._current_background = image_name

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
        pos = self.surface.get_rect().center
        return image.get_rect(center=pos) if image else pos

    def _left_pos(self, image):
        """
        Return the position of the given image to be put on the left of the screen
        """
        pos = (self.surface.get_rect().centerx // 2, self.surface.get_rect().centery)
        return image.get_rect(center=pos) if image else pos

    def _right_pos(self, image):
        """
        Return the position of the given image to be put on the right of the screen
        """
        pos = (self.surface.get_rect().centerx + self.surface.get_rect().centerx // 2, self.surface.get_rect().centery)
        return image.get_rect(center=pos) if image else pos

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
            self._update_background(self._current_background)
        pygame.display.update()

    def show_intro(self, image=None):
        """Show introduction view.
        """
        self._update_background("intro.png")
        self._update_foreground(image, 'right')
        pygame.display.update()

    def show_choice(self, number):
        """Show the choice view.
        """
        self._update_background("choice{}.png".format(number))
        pygame.display.update()

    def show_work_in_progress(self):
        """Show wait view.
        """
        self._picture_number = (0, self._picture_number[1])
        self._update_background("processing.png")
        pygame.display.update()

    def show_print(self, image=None):
        """Show print view.
        """
        self._picture_number = (0, self._picture_number[1])
        self._update_background("print.png")
        self._update_foreground(image, 'left')
        pygame.display.update()

    def show_finished(self):
        """Show finished view.
        """
        self._picture_number = (0, self._picture_number[1])
        self._update_background("finished.png")
        pygame.display.update()

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
        """Set window to full screen or initial size.
        """
        if self.is_fullscreen:
            self.is_fullscreen = False  # Set before get size
            pygame.mouse.set_visible(True)
            self.surface = pygame.display.set_mode(self.size, pygame.RESIZABLE)
        else:
            self.is_fullscreen = True  # Set before get size
            pygame.mouse.set_visible(False)
            self.surface = pygame.display.set_mode(self.size, pygame.FULLSCREEN)

        if self._current_background:
            self._update_background(self._current_background)
        else:
            self._update_picture_number()

        pygame.display.update()
