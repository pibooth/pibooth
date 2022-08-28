# -*- coding: utf-8 -*-

"""Base classes for view management.
"""

import pygame
from pibooth.utils import LOGGER


class BaseScene(object):
    """Base class for scene."""

    def __init__(self, name):
        self.name = name


class BaseWindow(object):

    """Base class for window.

    The following attributes are available for use in plugins:

    :attr is_fullscreen: True if the window is display in full screen
    :type is_fullscreen: bool
    :attr is_flash_on: True if the flash is ON
    :type is_flash_on: bool
    """

    FULLSCREEN = 'fullscreen'
    ARROW_TOP = 'top'
    ARROW_BOTTOM = 'bottom'
    ARROW_HIDDEN = 'hidden'
    ARROW_TOUCH = 'touchscreen'

    def __init__(self,
                 size=(800, 480),
                 bg_color=(0, 0, 0),
                 text_color=(255, 255, 255),
                 arrow_location=ARROW_BOTTOM,
                 arrow_offset=0,
                 debug=False):
        self.__size = size

        self.debug = debug
        self.bg_color = bg_color
        self.text_color = text_color
        self.arrow_location = arrow_location
        self.arrow_offset = arrow_offset
        self.print_number = 0
        self.print_failure = False
        self.capture_number = 0
        self.capture_max = 4

        self.is_fullscreen = False
        self.is_flash_on = False
        self.is_menu_shown = False

        self.scenes = {}
        self.scene = None

    def _create_scene(self, name):
        """Create scene instance."""
        raise NotImplementedError

    def add_scene(self, name):
        """Add a scene to the internal dictionary.
        """
        self.scenes[name] = self._create_scene(name)

    def remove_scene(self, name):
        """Remove a scene from the internal dictionary.
        """
        self.scenes.pop(name, None)

    def set_scene(self, name):
        """Set the current scene.
        """
        if name not in self.scenes:
            raise ValueError('"{}" not in registered scenes...'.format(name))

        LOGGER.debug("Set scene '%s'", name)
        self.scene = self.scenes[name]

    def get_rect(self, absolute=False):
        """Return a Rect object (as defined in pygame) for this window.

        :param absolute: absolute position considering the window centered on screen
        :type absolute: bool
        """
        return pygame.Rect(0, 0, self.__size[0], self.__size[1])

    def resize(self, size):
        """Resize the window only if not fullscreen.
        """
        if not self.is_fullscreen:
            self.__size = size  # Manual resizing

    def update(self, events):
        """Update sprites according to Pygame events.

        :param events: list of events to process.
        :type events: list
        """
        pass

    def draw(self):
        """Draw all Sprites on surface and return updated Pygame rects.
        """
        pass

    def set_capture_number(self, current_nbr, total_nbr):
        """Set the current number of captures taken.
        """
        assert total_nbr > 0, "Total number of captures shall be greater than 0"
        assert current_nbr <= total_nbr, "Current number of captures shall be lower or equal to total number"
        self.capture_number = current_nbr
        self.capture_max = total_nbr

    def set_print_number(self, current_nbr=None, failure=None):
        """Set the current number of tasks in the printer queue.
        """
        assert current_nbr >= 0, "Current number of printed files shall be greater or equal to 0"
        self.print_number = current_nbr
        self.print_failure = failure

    def toggle_flash(self):
        """Set flash to ON or OFF.
        """
        self.is_flash_on = not self.is_flash_on

    def toggle_fullscreen(self):
        """Set window to full screen or initial size.
        """
        self.is_fullscreen = not self.is_fullscreen

    def toggle_menu(self):
        """Show/hide settings menu.
        """
        self.is_menu_shown = not self.is_menu_shown
