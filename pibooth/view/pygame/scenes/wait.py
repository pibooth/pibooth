# -*- coding: utf-8 -*-

import os.path as osp
import pygame
from pibooth import pictures
from pibooth.view.base import BaseScene


class Background(pygame.sprite.DirtySprite):
    """Background of the window.
    """

    def __init__(self, size):
        """
        :param size: size tuple (width, height) of the background.
        """
        super(Background, self).__init__()
        self.image = pygame.Surface(size, pygame.SRCALPHA, 32)
        self.rect = pygame.Rect((0, 0), size)
        self.color = None
        self.path = None

    def render(self):
        """Draw background if has changed.
        """
        if self.dirty == 1:
            if self.color:
                self.image = pygame.Surface(self.rect.size, pygame.SRCALPHA, 32)
                self.image.fill(self.color)
            else:
                self.image = pictures.get_pygame_image(self.path, self.rect.size, crop=True, color=None)

    def set_skin(self, color_or_path):
        """Set background color (RGB tuple) or path to an image that used to
        fill the background.

        :param color_or_path: RGB color tuple or image path
        :type color_or_path: tuple or str
        """
        if isinstance(color_or_path, str):
            assert osp.isfile(color_or_path), "Invalid path for window background: '{}'".format(color_or_path)
            if color_or_path != self.path:
                self.color, self.path = None, color_or_path
                self.dirty = 1
        else:
            assert len(color_or_path) == 3, "Length of 3 is required for RGB tuple"
            if color_or_path != self.color:
                self.color, self.path = color_or_path, None
                self.dirty = 1

    def set_rect(self, x, y, width, height):
        """Set the background absolute position and size.

        :param x: position x.
        :param y: position y.
        :param width: background width.
        :param height: background height.
        """
        if self.rect.topleft != (x, y):
            self.rect.topleft = (x, y)
            self.dirty = 1
        if self.rect.size != (width, height):
            self.rect.size = (width, height)
            self.image = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            self.dirty = 1


class BasePygameScene(BaseScene):

    BACKGROUND = None

    def __init__(self, name):
        super(BasePygameScene, self).__init__(name)
        self.surface = None
        self.sprites = pygame.sprite.LayeredDirty()

    @property
    def background(self):
        return BasePygameScene.BACKGROUND

    def set_background(self, color_or_path, size):
        if not BasePygameScene.BACKGROUND:
            BasePygameScene.BACKGROUND = Background(size)
            self.sprites.add(BasePygameScene.BACKGROUND, layer=0)
        self.background.set_rect(0, 0, size[0], size[1])
        self.background.set_skin(color_or_path)
        self.background.render()
        self.sprites.clear(None, self.background.image)

    def update(self, events):
        """Pygame events processing callback method.
        ----------
        :param events: list of events to process.
        """
        self.sprites.update(events)

    def draw(self, surface):
        """Draw the elements on scene.

        This method is optimized to be called at each loop of the
        main application. It uses DirtySprite to update only parts
        of the screen that need to be refreshed.

        The first call to this method will setup the "eraser" surface that
        will be used to redraw dirty parts of the screen.

        :param surface: surface this scene will be displayed at
        :return: list of updated area
        """
        return self.sprites.draw(surface)

    def set_debug(self, enable=True):
        pass

    def set_image(self, image=None):
        pass

    def set_text_color(self, color):
        pass

    def set_arrow_offset(self, offset):
        pass

    def set_arrow_location(self, location):
        pass

    def set_print_number(self, current_nbr=None, failure=False):
        pass


class WaitScene(BasePygameScene):
    pass

    def update_print_action(self, enabled=True):
        pass
