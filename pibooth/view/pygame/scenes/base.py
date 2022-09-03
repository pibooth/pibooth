# -*- coding: utf-8 -*-

import os.path as osp
import PIL
import pygame

from pibooth import pictures
from pibooth.view.base import BaseScene


class OutlineSprite(pygame.sprite.DirtySprite):
    """Outline Sprite.
    """

    def __init__(self, sprite, color=(255, 0, 0)):
        """
        :param rect: rect of the outlined sprite
        :type rect: tuple
        :param color: RGB color tuple for the outline
        :type color: tuple
        """
        super(OutlineSprite, self).__init__()
        self.image = None
        self.rect = sprite.rect
        self.color = color
        sprite.outlines = self

    def render(self):
        """Draw outlines if has changed.
        """
        self.dirty = 1
        self.image = pygame.Surface(self.rect.size, pygame.SRCALPHA, 32)
        pygame.draw.rect(self.image, self.color, self.rect, 2)


class ImageSprite(pygame.sprite.DirtySprite):
    """Image Sprite.
    """

    def __init__(self, size, path=None, color=None):
        """
        :param size: size tuple (width, height) of the image.
        :type size: tuple
        :param path: image file path
        :type path: str
        :param color: RGB color tuple for the background
        :type color: tuple
        """
        super(ImageSprite, self).__init__()
        self.image = None
        self.image_orig = None
        self.rect = pygame.Rect((0, 0), size)
        self.color = color
        self.path = path
        self.outlines = None
        self.crop = False

    def render(self):
        """Draw image if has changed.
        """
        if self.image is None:
            if self.color:
                self.image = pygame.Surface(self.rect.size, pygame.SRCALPHA, 32)
                self.image.fill(self.color)
            else:
                if isinstance(self.image_orig, PIL.Image.Image):
                    surface = pygame.image.frombuffer(self.image_orig.tobytes(),
                                                      self.image_orig.size, self.image_orig.mode)
                    self.image = pictures.resize_pygame_image(surface, self.rect.size, crop=self.crop)
                else:
                    self.image = pictures.resize_pygame_image(self.image_orig, self.rect.size, crop=self.crop)

            if self.outlines:
                self.outlines.render()

    def set_skin(self, skin, crop=False):
        """Fill the sprite using a color (RGB tuple), path to an image or a PIL image.

        :param skin: image file path, RGB color tuple or PIL image
        :type skin: str or tuple or object
        :param crop: crop image to fit aspect ratio of the size
        :type crop: bool
        """
        if crop != self.crop:
            self.crop = crop
            self.dirty = 1

        if isinstance(skin, str):
            assert osp.isfile(skin), "Invalid path for window background: '{}'".format(skin)
            if skin != self.path:
                self.color, self.path, self.image = None, skin, None
                self.image_orig = pictures.get_pygame_image(self.path, color=None)
                self.dirty = 1
        elif isinstance(skin, (tuple, list)):
            assert len(skin) == 3, "Length of 3 is required for RGB tuple"
            if skin != self.color:
                self.color, self.path, self.image = skin, None, None
                self.dirty = 1
        else:
            assert isinstance(skin, PIL.Image.Image), "PIL Image is required"
            if skin != self.image_orig:
                self.color, self.path, self.image = None, None, None
                self.image_orig = skin
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
            self.image = None
            self.dirty = 1


class BasePygameScene(BaseScene):

    """Base class for Pygame scene. It use dirty sprite mechanism to
    save CPU usage. 4 layers are defined:

      - 0: one background sprite
      - 1: texts sprites
      - 2: one image sprite
      - 3: arrows sprites
      - 4: outlines sprites
    """

    BACKGROUND = None

    def __init__(self, name):
        super(BasePygameScene, self).__init__(name)
        self.sprites = pygame.sprite.LayeredDirty()
        self.image = ImageSprite((200, 200))
        self.image.visible = 0
        self.sprites.add(self.image, layer=2)
        self.sprites.add(OutlineSprite(self.image), layer=4)

    @property
    def background(self):
        return BasePygameScene.BACKGROUND

    def set_background(self, color_or_path, size):
        """Set background sprite.

        :param color_or_path: color of path to an imgae
        :type color_or_path: tuple or str
        :param size: size tuple (width, height) of the image.
        :type size: tuple
        """
        if not BasePygameScene.BACKGROUND:
            BasePygameScene.BACKGROUND = ImageSprite(size)
            self.sprites.add(BasePygameScene.BACKGROUND, layer=0)
        self.background.set_rect(0, 0, size[0], size[1])
        self.background.set_skin(color_or_path, crop=True)
        self.background.render()
        self.sprites.clear(None, self.background.image)

    def set_outlines(self, enable=True):
        """Draw outlines for each rectangle available for drawing
        images and texts.

        :param enable: enable / disable outlines
        :type enable: bool
        """
        for sprite in self.sprites.get_sprites_from_layer(4):
            if enable and not sprite.visible:
                sprite.visible = 1
            elif not enable and sprite.visible:
                sprite.visible = 0

    def set_image(self, image=None):
        """Set an image to the main place or hide it.
        """
        if image:
            self.image.set_skin(image)
            self.image.render()
            self.image.visible = 1
        elif self.image.visible:
            self.image.visible = 0

    def set_arrows(self, location, offset):
        """Set arrows attributes.
        """
        for sprite in self.sprites.get_sprites_from_layer(3):
            sprite.set_location(location)
            sprite.set_offset(offset)

    def set_text_color(self, color):
        pass

    def set_print_number(self, current_nbr=None, failure=False):
        pass

    def update(self, events):
        """Pygame events processing callback method.

        :param events: list of events to process.
        :type events: list
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
