# -*- coding: utf-8 -*-

"""Base classes for view management.
"""

import pygame
from pibooth.utils import LOGGER


class BaseScene(object):
    """Base class for scene."""

    ARROW_TOP = 'top'
    ARROW_BOTTOM = 'bottom'
    ARROW_HIDDEN = 'hidden'
    ARROW_TOUCH = 'touchscreen'

    def __init__(self, name):
        self.name = name

    def set_outlines(self, enable=True):
        raise NotImplementedError

    def set_image(self, image=None):
        raise NotImplementedError

    def set_background(self, color_or_path, size):
        raise NotImplementedError

    def set_text_color(self, color):
        raise NotImplementedError

    def set_arrows(self, location, offset):
        raise NotImplementedError

    def set_print_number(self, current_nbr=None, failure=False):
        raise NotImplementedError


class BaseWindow(object):

    """Base class for window.

    The following attributes are available for use in plugins:

    :attr is_fullscreen: True if the window is display in full screen
    :type is_fullscreen: bool
    """

    FULLSCREEN = 'fullscreen'

    def __init__(self,
                 size=(800, 480),
                 background=(0, 0, 0),
                 text_color=(255, 255, 255),
                 arrow_location=BaseScene.ARROW_BOTTOM,
                 arrow_offset=0,
                 debug=False):
        self._size = size

        self.debug = debug
        self.text_color = text_color
        self.bg_color_or_path = background
        self.arrow_location = arrow_location
        self.arrow_offset = arrow_offset
        self.print_number = 0
        self.print_failure = False

        self.is_fullscreen = False
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
        self.scene.set_outlines(self.debug)
        self.scene.set_background(self.bg_color_or_path, self._size)
        self.scene.set_text_color(self.text_color)
        self.scene.set_arrows(self.arrow_location, self.arrow_offset)
        self.scene.set_print_number(self.print_number, self.print_failure)

    def get_rect(self, absolute=False):
        """Return a Rect object (as defined in pygame) for this window.

        :param absolute: absolute position considering the window centered on screen
        :type absolute: bool
        """
        return pygame.Rect(0, 0, self._size[0], self._size[1])

    def resize(self, size):
        """Resize the window only if not fullscreen.
        """
        if not self.is_fullscreen:
            self._size = size  # Manual resizing

    def eventloop(self, app_update):
        """Main GUI events loop (blocking).

        :param app_update: function update application state
        :type app_update: callable
        """
        raise NotImplementedError

    # ---------------------------------------------------------------------
    # Functions applicable to more than one scene

    def set_image(self, pil_image=None):
        """Set the current displayed image.
        """
        self.scene.set_image(pil_image)

    def set_print_number(self, current_nbr=None, failure=False):
        """Set the current number of tasks in the printer queue.
        """
        assert current_nbr >= 0, "Current number of printed files shall be greater or equal to 0"
        self.print_number = current_nbr
        self.print_failure = failure

    def toggle_fullscreen(self):
        """Set window to full screen or initial size.
        """
        self.is_fullscreen = not self.is_fullscreen

    def toggle_menu(self):
        """Show/hide settings menu.
        """
        self.is_menu_shown = not self.is_menu_shown
