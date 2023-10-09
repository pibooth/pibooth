# -*- coding: utf-8 -*-

"""Base classes for view management.
"""

import pygame
from pibooth.utils import LOGGER


class BaseScene:
    """Base class for scene.

    Methodes defined here are abstarct and shall be implemented in child classes.
    Plugins will use them to set severals parameters depending on the pibooth
    configuration / user choices / new behaviors.
    """

    ARROW_TOP = 'top'
    ARROW_BOTTOM = 'bottom'
    ARROW_HIDDEN = 'hidden'
    ARROW_TOUCH = 'touchscreen'

    def resize(self, size):
        """Recalculate sizes of elements according to the new given size.

        :param size: new size of the scene
        :type size: tuple
        """
        raise NotImplementedError

    def set_outlines(self, enable=True):
        """Draw outlines for each rectangle available for drawing
        images and texts.

        :param enable: enable / disable outlines
        :type enable: bool
        """
        raise NotImplementedError

    def set_image(self, image=None, stream=False):
        """Set an image to the main place or hide it.

        :param image: image to set (path, PIL object or pygame object)
        :type image: str or object
        :param stream: optimize to process an images sequence
        :type stream: bool
        """
        raise NotImplementedError

    def set_text_color(self, color):
        """Set text font color.

        :param color: RGB color tuple for the texts
        :type color: tuple
        """
        raise NotImplementedError

    def set_arrows(self, location, offset):
        """Set arrows attributes.

        :param location: arrow location: ARROW_HIDDEN, ARROW_BOTTOM, ARROW_TOP, ARROW_TOUCH
        :type location: str
        :param offset: x offset from current position to screen outer
        :type offset: int
        """
        raise NotImplementedError


class BaseWindow:

    """Base class for window.

    :py:class:`BaseWindow` emits the following events consumed by plugins:

    - EVT_PIBOOTH_CAPTURE
    - EVT_PIBOOTH_PRINT
    - EVT_PIBOOTH_SETTINGS

    The following attributes are available for use in plugins (``win`` reprensents
    the BaseWindow instance):

    - ``win.type`` (str): name of the graphical backend library (``nogui`` or ``pygame``)
    - ``win.text_color`` (tuple): RGB color tuple used for texts
    - ``win.bg_color_or_path`` (tuple/str): RGB color tuple or path to image used for background
    - ``win.is_fullscreen`` (bool): True if the window is display in full screen
    - ``win.is_menu_shown`` (bool): True if the settings menu is displayed
    """

    FULLSCREEN = 'fullscreen'

    def __init__(self,
                 size=(800, 480),
                 background=(0, 0, 0),
                 text_color=(255, 255, 255),
                 arrow_location=BaseScene.ARROW_BOTTOM,
                 arrow_offset=0,
                 debug=False):
        self._size = size  # Size of the window when not fullscreen
        self.debug = debug
        self.arrow_location = arrow_location
        self.arrow_offset = arrow_offset
        self.scenes = {}
        self.scene = None

        # ---------------------------------------------------------------------
        # Variables shared with plugins
        # Change them may break plugins compatibility
        self.type = None
        self.text_color = text_color
        self.bg_color_or_path = background
        self.is_fullscreen = False
        self.is_menu_shown = False
        # ---------------------------------------------------------------------

    def add_scene(self, scene):
        """Add a scene to the internal dictionary.

        :param scene: scene to add
        :type scene: sub-class instance of BaseScene
        """
        assert isinstance(scene, BaseScene), "Scene shall inherite from BaseScene"
        assert isinstance(scene.name, str) and len(scene.name) > 0, "Scene name shall be defined"
        self.scenes[scene.name] = scene

    def remove_scene(self, name):
        """Remove a scene from the internal dictionary.
        """
        self.scenes.pop(name, None)

    def set_scene(self, name):
        """Set the current scene.
        """
        if name not in self.scenes:
            raise ValueError(f"'{name}' not in registered scenes...")

        LOGGER.debug("Set scene '%s'", name)
        self.scene = self.scenes[name]
        self.scene.set_outlines(self.debug)
        self.scene.set_text_color(self.text_color)
        self.scene.set_arrows(self.arrow_location, self.arrow_offset)
        self.resize(self._size)  # Force graphical element to be recalculated

    def set_menu(self, app, cfg, pm):
        """Set the menu.
        """
        pass

    def resize(self, size):
        """Resize the window only if not fullscreen.

        :param size: new size of the scene
        :type size: tuple
        """
        if not self.is_fullscreen:
            self._size = size  # Size of the window when not fullscreen

        # Call get_rect() to take new computed size if != self._size
        if self.scene:
            self.scene.resize(self.get_rect().size)

    def get_rect(self, absolute=False):
        """Return a Rect object (as defined in pygame) for this window.

        :param absolute: absolute position considering the window centered on screen
        :type absolute: bool
        """
        return pygame.Rect(0, 0, self._size[0], self._size[1])

    def eventloop(self, app_update):
        """Main GUI events loop (blocking).

        :param app_update: function update application state
        :type app_update: callable
        """
        raise NotImplementedError

    # ---------------------------------------------------------------------
    # Functions applicable to more than one scene

    def set_background(self, color_or_path):
        """Set background sprite.

        :param color_or_path: color of path to an imgae
        :type color_or_path: tuple or str
        """
        pass

    def set_system_status(self, printer_queue_size=None, printer_failure=None, total_printed=None, total_taken=None):
        """Set the current number of tasks in the printer queue.
        """
        pass

    def toggle_fullscreen(self):
        """Set window to full screen or initial size.
        """
        self.is_fullscreen = not self.is_fullscreen

    def toggle_menu(self):
        """Show/hide settings menu.
        """
        self.is_menu_shown = not self.is_menu_shown
