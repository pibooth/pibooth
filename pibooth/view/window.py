# -*- coding: utf-8 -*-

"""Pibooth view management.
"""

import os
import pygame
from pygame import gfxdraw
from PIL import Image
import pygame_menu as pgm
import pygame_vkeyboard as vkb
from pibooth import pictures, fonts, evtfilters
from pibooth.view import background
from pibooth.view.menu import PiConfigMenu
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
        if 'SDL_VIDEO_WINDOW_POS' not in os.environ:
            os.environ['SDL_VIDEO_CENTERED'] = '1'
        pygame.init()

        # Save the desktop mode, shall be done before `setmode` (SDL 1.2.10, and pygame 1.8.0)
        info = pygame.display.Info()

        pygame.display.set_caption(title)
        self.is_fullscreen = False
        self.display_size = (info.current_w, info.current_h)
        self.surface = pygame.display.set_mode(self.__size, pygame.RESIZABLE)

        self._menu = PiConfigMenu(plugins_manager, configuration, application, self)

        self._keyboard = vkb.VKeyboard(self.surface,
                                       self._on_keyboard_event,
                                       vkb.VKeyboardLayout(vkb.VKeyboardLayout.QWERTY),
                                       renderer=vkb.VKeyboardRenderer.DARK,
                                       show_text=True,
                                       joystick_navigation=True)
        self._keyboard.disable()
        self._print_failure = False
        self._capture_number = (0, 4)  # (current, max)
        self._is_flash_on = False

        # Don't use pygame.mouse.get_cursor() because will be removed in pygame2
        self._cursor = ((16, 16), (0, 0),
                        (0, 0, 64, 0, 96, 0, 112, 0, 120, 0, 124, 0, 126, 0, 127, 0,
                         127, 128, 124, 0, 108, 0, 70, 0, 6, 0, 3, 0, 3, 0, 0, 0),
                        (192, 0, 224, 0, 240, 0, 248, 0, 252, 0, 254, 0, 255, 0, 255,
                         128, 255, 192, 255, 224, 254, 0, 239, 0, 207, 0, 135, 128, 7, 128, 3, 0))

    def update(self, evts):
        """Pygame events processing.

        :param evts: list of events to process.
        :type evts: list
        """
        for evt in evts:
            if evtfilters.is_resize_event(evt):
                self.resize(evt.size)
            elif evtfilters.is_fullscreen_event(evt):
                self.toggle_fullscreen()
            elif evtfilters.is_settings_event(evt):
                self.toggle_menu()
            elif evtfilters.is_print_button_event(evt, self):
                # Convert HW button events to keyboard events for menu
                event = evtfilters.create_click_event()
                LOGGER.debug("EVT_BUTTONDOWN: generate MENU-APPLY event")
                evts += (event,)

        if self._menu.is_shown():

            self._menu.update(evts)

    def draw(self):
        """Draw all Sprites.
        """
        return []

    def get_rect(self, absolute=False):
        """Return a Rect object (as defined in pygame) for this window.

        :param absolute: absolute position considering the window centered on screen
        :type absolute: bool
        """
        if absolute:
            return self.surface.get_rect(center=(self.display_size[0] / 2, self.display_size[1] / 2))
        return self.surface.get_rect()

    def resize(self, size):
        """Resize the window keeping aspect ratio.
        """
        if not self.is_fullscreen:
            self.__size = size  # Manual resizing
            self.surface = pygame.display.set_mode(self.__size, pygame.RESIZABLE)

    def is_menu_shown(self):
        return self._menu.is_shown()

    def show_oops(self):
        """Show failure view in case of exception.
        """
        self._capture_number = (0, self._capture_number[1])
        print("Oops")

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

    def set_capture_number(self, current_nbr, total_nbr):
        """Set the current number of captures taken.
        """
        if total_nbr < 1:
            raise ValueError("Total number of captures shall be greater than 0")

        if self._capture_number != (current_nbr, total_nbr):
            self._capture_number = (current_nbr, total_nbr)
            self._update_background(background.CaptureBackground())
            if self._current_foreground:
                self._update_foreground(*self._current_foreground)

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

    def toggle_flash(self):
        """Update background in white.
        """
        if not self._is_flash_on:
            self.surface.fill((255, 255, 255))
            if self._current_foreground:
                # Flash only the background, keep foreground at the top
                self._update_foreground(*self._current_foreground)
        else:
            self._update()
        self._is_flash_on = not self._is_flash_on

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

    def toggle_menu(self):
        """Show/hide settings menu.
        """
        if self._menu.is_shown():
            self._menu.show()
        else:
            self._menu.hide()
