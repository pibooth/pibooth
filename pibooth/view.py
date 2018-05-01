# -*- coding: utf-8 -*-

import time
import contextlib
import pygame
from pygame import gfxdraw
from PIL import Image
from pibooth.pictures import background
from pibooth.utils import LOGGER
from pibooth.pictures import sizing


class PtbWindow(object):

    """Manage the window.
    """

    CENTER = 'center'
    RIGHT = 'right'
    LEFT = 'left'

    def __init__(self, title, size):
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
        self.display_size = (info.current_w, info.current_h)
        self.surface = pygame.display.set_mode(self.__size, pygame.RESIZABLE)

        self._buffered_images = {}
        self._current_background = None
        self._current_foreground = None
        self._picture_number = (0, 4)  # (current, max)

        self._pos_map = {self.CENTER: self._center_pos,
                         self.RIGHT: self._right_pos,
                         self.LEFT: self._left_pos}

        if isinstance(size, str) and size.lower() == 'fullscreen':
            self.toggle_fullscreen()

    def _update_foreground(self, pil_image, pos=CENTER, resize=True):
        """Show a PIL image on the foreground.
        Only once is bufferized to avoid memory leak.
        """
        image_name = id(pil_image)

        image_size_max = (2 * self.size[1] // 3, self.size[1])

        buff_size, buff_image = self._buffered_images.get(image_name, (None, None))
        if buff_image and image_size_max == buff_size:
            image = buff_image
            LOGGER.debug("Use buffered image '%s'", image_name)
        else:
            if resize:
                image = pil_image.resize(sizing.new_size_keep_aspect_ratio(pil_image.size, image_size_max), Image.ANTIALIAS)
            else:
                image = pil_image
            image = pygame.image.fromstring(image.tobytes(), image.size, image.mode)
            if self._current_foreground:
                self._buffered_images.pop(id(self._current_foreground[0]), None)
            LOGGER.debug("Add to buffer the image '%s'", image_name)
            self._buffered_images[image_name] = (image_size_max, image)

        self._current_foreground = (pil_image, pos, resize)
        self.surface.blit(image, self._pos_map[pos](image))

    def _update_background(self, bkgd):
        """Show image on the background.
        """
        self._current_background = self._buffered_images.setdefault(str(bkgd), bkgd)
        self._current_background.resize(self.surface)
        self._current_background.paint(self.surface)
        self._update_picture_number()

    def _update_picture_number(self):
        """Update the pictures counter displayed.
        """
        if not self._picture_number[0]:
            return  # Dont show counter: no picture taken
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

    def _center_pos(self, image):
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
        self.update()

    def update(self):
        """Repaint the window with currently displayed images.
        """
        if self._current_background:
            self._update_background(self._current_background)
        else:
            self._update_picture_number()
        if self._current_foreground:
            self._update_foreground(*self._current_foreground)
        pygame.display.update()

    def show_oops(self):
        """Show failure view in case of exception.
        """
        self._picture_number = (0, self._picture_number[1])
        self._update_background(background.OopsBackground())
        pygame.display.update()

    def show_intro(self, pil_image=None, with_print=True):
        """Show introduction view.
        """
        self._picture_number = (0, self._picture_number[1])
        if with_print and pil_image:
            self._update_background(background.IntroWithPrintBackground())
        else:
            self._update_background(background.IntroBackground())

        if pil_image:
            self._update_foreground(pil_image, self.RIGHT)
        pygame.display.update()

    def show_choice(self, choices, selected=None):
        """Show the choice view.
        """
        self._picture_number = (0, self._picture_number[1])
        if not selected:
            self._update_background(background.ChooseBackground(choices))
        else:
            self._update_background(background.ChosenBackground(choices, selected))

        pygame.display.update()

    def show_image(self, pil_image=None, pos=CENTER):
        """Show PIL image as it (no resize).
        """
        if not pil_image:
            # Clear the currently displayed image
            if self._current_foreground:
                self._buffered_images.pop(id(self._current_foreground[0]), None)
                self._current_foreground = None
        else:
            self._update_foreground(pil_image, pos, False)
        pygame.display.update()

    def show_work_in_progress(self):
        """Show wait view.
        """
        self._picture_number = (0, self._picture_number[1])
        self._update_background(background.ProcessingBackground())
        pygame.display.update()

    def show_print(self, pil_image=None):
        """Show print view.
        """
        self._picture_number = (0, self._picture_number[1])
        self._update_background(background.PrintBackground())
        if pil_image:
            self._update_foreground(pil_image, self.LEFT)
        pygame.display.update()

    def show_finished(self):
        """Show finished view.
        """
        self._picture_number = (0, self._picture_number[1])
        self._update_background(background.FinishedBackground())
        pygame.display.update()

    @contextlib.contextmanager
    def flash(self, count):
        """Flash the window content.
        """
        if count < 1:
            raise ValueError("The flash counter shall be greater than 0")

        for i in range(count):
            self.surface.fill((255, 255, 255))
            if self._current_foreground:
                # Flash only the background, keep forground at the top
                self._update_foreground(*self._current_foreground)
            pygame.display.update()
            pygame.event.pump()
            time.sleep(0.02)
            if i == count - 1:
                yield  # Let's doing actions before end of flash
                self.update()
                pygame.event.pump()
            else:
                self.update()
                pygame.event.pump()
                time.sleep(0.02)

    def set_picture_number(self, current_nbr, total_nbr):
        """Set the current number of pictures taken.
        """
        if total_nbr < 1:
            raise ValueError("Total number of captures shall be greater than 0")

        self._picture_number = (current_nbr, total_nbr)
        self._update_background(background.CaptureBackground())
        if self._current_foreground:
            self._update_foreground(*self._current_foreground)
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

        self.update()
