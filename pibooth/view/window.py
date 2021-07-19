# -*- coding: utf-8 -*-

"""Pibooth view management.
"""

import os
import time
import contextlib
import pygame
from pygame import gfxdraw
from PIL import Image
from pibooth import pictures, fonts
from pibooth.view import background
from pibooth.utils import LOGGER
from pibooth.pictures import sizing


class PiWindow(object):

    """Class to handle the window.
    The following attributes are available for use in plugins:

    :attr surface: surface on which sprites are displayed
    :type surface: :py:class:`pygame.Surface`
    :attr is_fullscreen: set to True if the window is display in full screen
    :type is_fullscreen: bool
    :attr display_size: tuple (width, height) represneting the size of the screen
    :type display_size: tuple
    """

    CENTER = 'center'
    RIGHT = 'right'
    LEFT = 'left'
    FULLSCREEN = 'fullscreen'

    def __init__(self, title,
                 size=(800, 480),
                 color=(0, 0, 0),
                 text_color=(255, 255, 255),
                 arrow_location=background.ARROW_BOTTOM,
                 arrow_offset=0,
                 debug=False):
        self.__size = size
        self.debug = debug
        self.bg_color = color
        self.text_color = text_color
        self.arrow_location = arrow_location
        self.arrow_offset = arrow_offset

        # Prepare the pygame module for use
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        pygame.init()

        # Save the desktop mode, shall be done before `setmode` (SDL 1.2.10, and pygame 1.8.0)
        info = pygame.display.Info()

        pygame.display.set_caption(title)
        self.is_fullscreen = False
        self.display_size = (info.current_w, info.current_h)
        self.surface = pygame.display.set_mode(self.__size, pygame.RESIZABLE)

        self._buffered_images = {}
        self._current_background = None
        self._current_foreground = None
        self._print_number = 0
        self._print_failure = False
        self._capture_number = (0, 4)  # (current, max)

        self._pos_map = {self.CENTER: self._center_pos,
                         self.RIGHT: self._right_pos,
                         self.LEFT: self._left_pos,
                         self.FULLSCREEN: self._center_pos}

        # Don't use pygame.mouse.get_cursor() because will be removed in pygame2
        self._cursor = ((16, 16), (0, 0),
                        (0, 0, 64, 0, 96, 0, 112, 0, 120, 0, 124, 0, 126, 0, 127, 0,
                         127, 128, 124, 0, 108, 0, 70, 0, 6, 0, 3, 0, 3, 0, 0, 0),
                        (192, 0, 224, 0, 240, 0, 248, 0, 252, 0, 254, 0, 255, 0, 255,
                         128, 255, 192, 255, 224, 254, 0, 239, 0, 207, 0, 135, 128, 7, 128, 3, 0))

    def _update_foreground(self, pil_image, pos=CENTER, resize=True):
        """Show a PIL image on the foreground.
        Only one is bufferized to avoid memory leak.
        """
        image_name = id(pil_image)

        if pos == self.FULLSCREEN:
            image_size_max = (self.surface.get_size()[0] * 0.9, self.surface.get_size()[1] * 0.9)
        else:
            image_size_max = (self.surface.get_size()[0] * 0.48, self.surface.get_size()[1])

        buff_size, buff_image = self._buffered_images.get(image_name, (None, None))
        if buff_image and image_size_max == buff_size:
            image = buff_image
        else:
            if resize:
                image = pil_image.resize(sizing.new_size_keep_aspect_ratio(
                    pil_image.size, image_size_max), Image.ANTIALIAS)
            else:
                image = pil_image
            image = pygame.image.frombuffer(image.tobytes(), image.size, image.mode)
            if self._current_foreground:
                self._buffered_images.pop(id(self._current_foreground[0]), None)
            LOGGER.debug("Add to buffer the image '%s'", image_name)
            self._buffered_images[image_name] = (image_size_max, image)

        self._current_foreground = (pil_image, pos, resize)

        if self.debug and resize:
            # Build rectangle around picture area for debuging purpose
            outlines = pygame.Surface(image_size_max, pygame.SRCALPHA, 32)
            pygame.draw.rect(outlines, pygame.Color(255, 0, 0), outlines.get_rect(), 2)
            self.surface.blit(outlines, self._pos_map[pos](outlines))

        return self.surface.blit(image, self._pos_map[pos](image))

    def _update_background(self, bkgd):
        """Show image on the background.
        """
        self._current_background = self._buffered_images.setdefault(str(bkgd), bkgd)
        self._current_background.set_color(self.bg_color)
        self._current_background.set_outlines(self.debug)
        self._current_background.set_text_color(self.text_color)
        self._current_background.resize(self.surface)
        self._current_background.paint(self.surface)
        self._update_capture_number()
        self._update_print_number()

    def _update_capture_number(self):
        """Update the captures counter displayed.
        """
        if not self._capture_number[0]:
            return  # Dont show counter: no picture taken

        center = self.surface.get_rect().center
        radius = 10
        border = 20
        x = center[0] - (2 * radius * self._capture_number[1] + border * (self._capture_number[1] - 1)) // 2
        y = self.surface.get_size()[1] - radius - border
        for nbr in range(self._capture_number[1]):
            gfxdraw.aacircle(self.surface, x, y, radius, self.text_color)
            if self._capture_number[0] > nbr:
                # Because anti-aliased filled circle doesn't exist
                gfxdraw.aacircle(self.surface, x, y, radius - 3, self.text_color)
                gfxdraw.filled_circle(self.surface, x, y, radius - 3, self.text_color)
            x += (2 * radius + border)

    def _update_print_number(self):
        """Update the number of files in the printer queue.
        """
        if not self._print_number and not self._print_failure:
            return  # Dont show counter: no file in queue, no failure

        smaller = self.surface.get_size()[1] if self.surface.get_size(
        )[1] < self.surface.get_size()[0] else self.surface.get_size()[0]
        side = int(smaller * 0.05)  # 5% of the window

        if side > 0:
            if self._print_failure:
                image = pictures.get_pygame_image('printer_failure.png', (side, side), color=self.text_color)
            else:
                image = pictures.get_pygame_image('printer.png', (side, side), color=self.text_color)
            y = self.surface.get_rect().height - image.get_rect().height - 10
            self.surface.blit(image, (10, y))
            font = pygame.font.Font(fonts.CURRENT, side)
            label = font.render(str(self._print_number), True, self.text_color)
            self.surface.blit(label, (side + 20, y))

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

    def get_rect(self, absolute=False):
        """Return a Rect object (as defined in pygame) for this window.

        :param absolute: absolute position considering the window centered on screen
        :type absolute: bool
        """
        if absolute:
            return self.surface.get_rect(center=(self.display_size[0] / 2, self.display_size[1] / 2))
        return self.surface.get_rect()

    def get_image(self):
        """Return the currently displayed foreground image.
        """
        if self._current_foreground:
            return self._current_foreground[0]
        return None

    def resize(self, size):
        """Resize the window keeping aspect ratio.
        """
        if not self.is_fullscreen:
            self.__size = size  # Manual resizing
            self.surface = pygame.display.set_mode(self.__size, pygame.RESIZABLE)
        self.update()

    def update(self):
        """Repaint the window with currently displayed images.
        """
        if self._current_background:
            self._update_background(self._current_background)
        else:
            self._update_capture_number()
            self._update_print_number()
        if self._current_foreground:
            self._update_foreground(*self._current_foreground)

    def show_oops(self):
        """Show failure view in case of exception.
        """
        self._capture_number = (0, self._capture_number[1])
        self._update_background(background.OopsBackground())

    def show_intro(self, pil_image=None, with_print=True):
        """Show introduction view.
        """
        self._capture_number = (0, self._capture_number[1])
        if with_print and pil_image:
            self._update_background(background.IntroWithPrintBackground(self.arrow_location, self.arrow_offset))
        else:
            self._update_background(background.IntroBackground(self.arrow_location, self.arrow_offset))

        if pil_image:
            self._update_foreground(pil_image, self.RIGHT)
        elif self._current_foreground:
            self._buffered_images.pop(id(self._current_foreground[0]), None)
            self._current_foreground = None

    def show_choice(self, choices, selected=None):
        """Show the choice view.
        """
        self._capture_number = (0, self._capture_number[1])
        if not selected:
            self._update_background(background.ChooseBackground(choices, self.arrow_location, self.arrow_offset))
        else:
            self._update_background(background.ChosenBackground(choices, selected))

    def show_image(self, pil_image=None, pos=CENTER):
        """Show PIL image as it (no resize).
        """
        if not pil_image:
            # Clear the currently displayed image
            if self._current_foreground:
                _, image = self._buffered_images.pop(id(self._current_foreground[0]))
                _, pos, _ = self._current_foreground
                self._current_foreground = None
                image.fill((0, 0, 0))
                return self.surface.blit(image, self._pos_map[pos](image))
        else:
            return self._update_foreground(pil_image, pos, False)

    def show_work_in_progress(self):
        """Show wait view.
        """
        self._capture_number = (0, self._capture_number[1])
        self._update_background(background.ProcessingBackground())

    def show_print(self, pil_image=None):
        """Show print view (image resized on the left).
        """
        self._capture_number = (0, self._capture_number[1])
        self._update_background(background.PrintBackground(self.arrow_location,
                                                           self.arrow_offset))
        if pil_image:
            self._update_foreground(pil_image, self.LEFT)

    def show_finished(self, pil_image=None):
        """Show finished view (image resized fullscreen).
        """
        self._capture_number = (0, self._capture_number[1])
        if pil_image:
            bg = background.FinishedWithImageBackground(pil_image.size)
            if self._buffered_images.get(str(bg), bg).foreground_size != pil_image.size:
                self._buffered_images.pop(str(bg))  # Drop cache, foreground size ratio has changed
            self._update_background(background.FinishedWithImageBackground(pil_image.size))
            self._update_foreground(pil_image, self.FULLSCREEN)
        else:
            self._update_background(background.FinishedBackground())

    @contextlib.contextmanager
    def flash(self, count):
        """Flash the window content.
        """
        if count < 1:
            raise ValueError("The flash counter shall be greater than 0")

        for i in range(count):
            self.surface.fill((255, 255, 255))
            if self._current_foreground:
                # Flash only the background, keep foreground at the top
                self._update_foreground(*self._current_foreground)
            pygame.event.pump()
            pygame.display.update()
            time.sleep(0.02)
            if i == count - 1:
                yield  # Let's do actions before end of flash
                self.update()
                pygame.event.pump()
                pygame.display.update()
            else:
                self.update()
                pygame.event.pump()
                pygame.display.update()
                time.sleep(0.02)

    def set_capture_number(self, current_nbr, total_nbr):
        """Set the current number of captures taken.
        """
        if total_nbr < 1:
            raise ValueError("Total number of captures shall be greater than 0")

        self._capture_number = (current_nbr, total_nbr)
        self._update_background(background.CaptureBackground())
        if self._current_foreground:
            self._update_foreground(*self._current_foreground)
        pygame.display.update()

    def set_print_number(self, current_nbr=None, failure=None):
        """Set the current number of tasks in the printer queue.
        """
        update = False

        if current_nbr is not None and self._print_number != current_nbr:
            self._print_number = current_nbr
            update = True

        if failure is not None and self._print_failure != failure:
            self._print_failure = failure
            update = True

        if update:
            self._update_background(self._current_background)
            if self._current_foreground:
                self._update_foreground(*self._current_foreground)
            pygame.display.update()

    def toggle_fullscreen(self):
        """Set window to full screen or initial size.
        """
        if self.is_fullscreen:
            self.is_fullscreen = False  # Set before resize
            pygame.mouse.set_cursor(*self._cursor)
            self.surface = pygame.display.set_mode(self.__size, pygame.RESIZABLE)
        else:
            self.is_fullscreen = True  # Set before resize
            # Make an invisible cursor (don't use pygame.mouse.set_visible(False) because
            # the mouse event will always return the window bottom-right coordinate)
            pygame.mouse.set_cursor((8, 8), (0, 0), (0, 0, 0, 0, 0, 0, 0, 0), (0, 0, 0, 0, 0, 0, 0, 0))
            self.surface = pygame.display.set_mode(self.display_size, pygame.FULLSCREEN)

        self.update()

    def drop_cache(self):
        """Drop all cached background and foreground to force
        refreshing the view.
        """
        self._current_background = None
        self._current_foreground = None
        self._buffered_images = {}
