# -*- coding: utf-8 -*-

import os.path as osp
import PIL
import pygame

from pibooth import pictures
from pibooth.view.base import BaseWindow, BaseScene


class OutlinesSprite(pygame.sprite.DirtySprite):
    """Outlines Sprite.
    """

    def __init__(self, sprite, color=(255, 0, 0)):
        """
        :param sprite: sprite on which outlines are drawn
        :type sprite: object
        :param color: RGB color tuple for the outlines
        :type color: tuple
        """
        super(OutlinesSprite, self).__init__()
        self.image = pygame.Surface((10, 10), pygame.SRCALPHA, 32)
        self.rect = sprite.rect
        self.color = color
        self.visible = 0
        self._sp = sprite
        self._sp.outlines = self

    def __repr__(self):
        return f"{self.__class__.__name__}(rect={tuple(self.rect)}"

    def show(self):
        """Show outlines (only if reference sprite is visible).
        """
        if self._sp.visible and not self.visible:
            self.visible = 1

    def hide(self):
        """Hide outlines.
        """
        if self.visible:
            self.visible = 0

    def render(self):
        """Draw outlines only if visible.
        """
        if self.visible:
            self.dirty = 1
            self.image = pygame.Surface(self.rect.size, pygame.SRCALPHA, 32)
            pygame.draw.rect(self.image, self.color, (0, 0, self.rect.width, self.rect.height), 2)


class ImageSprite(pygame.sprite.DirtySprite):
    """Image Sprite.
    """

    def __init__(self, skin=None, size=(10, 10)):
        """
        :param skin: image file path, RGB color tuple,  PIL image or Pygame surface
        :type skin: str or tuple or object
        :param size: size tuple (width, height) of the image.
        :type size: tuple
        """
        super(ImageSprite, self).__init__()
        self.image = None
        self.image_orig = None
        self.rect = pygame.Rect((0, 0), size)
        self.color = None
        self.path = None
        self.outlines = None  # Set by OutlinesSprite class
        self.crop = False
        self.hflip = False
        self.vflip = False
        self.angle = 0
        if skin:
            self.set_skin(skin)

    def __repr__(self):
        if self.path:
            path = osp.basename(self.path)
        else:
            path = ''
        return f"{self.__class__.__name__}(path='{path}', rect={tuple(self.rect)})"

    def show(self):
        """Show image.
        """
        if not self.visible:
            self.visible = 1
        if self.outlines:
            self.outlines.show()

    def hide(self):
        """Hide image.
        """
        if self.visible:
            self.visible = 0
        if self.outlines:
            self.outlines.hide()

    def render(self):
        """Draw image if has changed and visible.
        """
        if self.image is None and self.visible:
            if isinstance(self.image_orig, (tuple, list)):
                self.image = pygame.Surface(self.rect.size, pygame.SRCALPHA, 32)
                self.image.fill(self.image_orig)
            elif isinstance(self.image_orig, PIL.Image.Image):
                surface = pygame.image.frombuffer(self.image_orig.tobytes(),
                                                  self.image_orig.size, self.image_orig.mode)
                self.image = pictures.transform_pygame_image(surface, self.rect.size, hflip=self.hflip,
                                                             vflip=self.vflip, angle=self.angle, crop=self.crop,
                                                             color=self.color)
            else:
                self.image = pictures.transform_pygame_image(self.image_orig, self.rect.size, hflip=self.hflip,
                                                             vflip=self.vflip, angle=self.angle, crop=self.crop,
                                                             color=self.color)

            if self.outlines:
                self.outlines.render()

    def set_skin(self, skin):
        """Set skin used to fill the sprite. Skin can be:

            - RGB color tuple
            - path to an image
            - PIL image object
            - Pygame surface object

        :param skin: image file path, RGB color tuple,  PIL image or Pygame surface
        :type skin: str or tuple or object
        """
        if isinstance(skin, str):
            if skin != self.path:
                self.path, self.image = skin, None  # Force rendering
                self.image_orig = pictures.load_pygame_image(self.path)
                self.dirty = 1
        elif isinstance(skin, (tuple, list)):
            assert len(skin) == 3, "Length of 3 is required for RGB tuple"
            if skin != self.image_orig:
                self.path, self.image = None, None  # Force rendering
                self.image_orig = skin
                self.dirty = 1
        else:
            assert isinstance(skin, (PIL.Image.Image, pygame.Surface)), "PIL Image or Pygame Surface is required"
            if skin != self.image_orig:
                self.path, self.image = None, None  # Force rendering
                self.image_orig = skin
                self.dirty = 1

    def set_crop(self, crop=True):
        """Crop the skin to fit sprite size.

        :param crop: crop image to fit aspect ratio of the size
        :type crop: bool
        """
        if crop != self.crop:
            self.crop = crop
            self.image = None  # Force rendering
            self.dirty = 1

    def set_flip(self, hflip=None, vflip=None):
        """Flip the skin vertically or horizontally.

        :param hflip: apply an horizontal flip
        :type hflip: bool
        :param vflip: apply a vertical flip
        :type vflip: bool
        """
        if hflip is not None and hflip != self.hflip:
            self.hflip = hflip
            self.image = None  # Force rendering
            self.dirty = 1
        if vflip is not None and vflip != self.vflip:
            self.vflip = vflip
            self.image = None  # Force rendering
            self.dirty = 1

    def set_angle(self, angle=0):
        """Rotate the skin.

        :param angle: angle of rotation of the image
        :type angle: int
        """
        if angle != self.angle:
            self.angle = angle
            self.image = None  # Force rendering
            self.dirty = 1

    def set_color(self, color):
        """Re-colorize the skin.

        :param angle: angle of rotation of the image
        :type angle: int
        """
        if color != self.color:
            self.color = color
            self.image = None  # Force rendering
            self.dirty = 1

    def set_rect(self, x, y, width, height):
        """Set the sprite absolute position and size.

        :param x: position x
        :param y: position y
        :param width: background width
        :param height: background height
        """
        if self.rect.topleft != (x, y):
            self.rect.topleft = (x, y)
            self.dirty = 1
        if self.rect.size != (width, height):
            self.rect.size = (width, height)
            self.image = None  # Force rendering
            self.dirty = 1

    def get_color(self):
        if self.color:
            return self.color
        else:
            return pygame.transform.average_color(self.image)


class TextSprite(pygame.sprite.DirtySprite):

    def __init__(self, text=None, size=(10, 10)):
        """
        :param size: size tuple (width, height) of the image.
        :type size: tuple
        :param path: image file path
        :type path: str
        """
        super(ImageSprite, self).__init__()
        self.image = None
        self.rect = pygame.Rect((0, 0), size)
        self.text = text
        self.color = None
        if text is not None:
            self.set_text(text)

    def set_color(self, color):
        """Re-colorize the skin.

        :param angle: angle of rotation of the image
        :type angle: int
        """
        if color != self.color:
            self.color = color
            self.image = None  # Force rendering
            self.dirty = 1


class ArrowSprite(ImageSprite):

    def __init__(self, *args, **kwargs):
        super(ArrowSprite, self).__init__(*args, **kwargs)
        self.location = BaseWindow.ARROW_BOTTOM
        self.offset = 0

    def set_location(self, location):
        if location != self.location:
            self.location = location
            self.dirty = 1

    def set_offset(self, offset):
        if offset != self.offset:
            self.offset = offset
            self.dirty = 1


class LeftArrowSprite(ArrowSprite):

    def __init__(self, *args, **kwargs):
        super(LeftArrowSprite, self).__init__(*args, **kwargs)
        self.set_skin('arrow.png')

    def set_location(self, location):
        super(LeftArrowSprite, self).set_location(location)
        if location == BaseWindow.ARROW_BOTTOM:
            self.set_flip(vflip=False)
            self.show()
        elif location == BaseWindow.ARROW_TOP:
            self.set_flip(vflip=True)
            self.show()
        else:
            self.hide()


class RightArrowSprite(LeftArrowSprite):

    def __init__(self, *args, **kwargs):
        super(RightArrowSprite, self).__init__(*args, **kwargs)
        self.set_flip(hflip=True)


class BasePygameScene(BaseScene):

    """Base class for Pygame scene. It use dirty sprite mechanism to
    save CPU usage.
    """

    BACKGROUND = None

    def __init__(self, name):
        super(BasePygameScene, self).__init__(name)
        self.sprites = pygame.sprite.LayeredDirty()
        self.image = ImageSprite()
        self.image.visible = 0
        self.add_sprite(self.image, layer=3)

    def add_sprite(self, sprite, outlines=True, layer=0):
        """Declare a new sprite to draw.

        Sprites are drawn as ordered. Four layers are defined:

            - 0: one background sprite
            - 1: texts sprites
            - 2: assets sprites
            - 3: one speciale image
            - 4: arrows sprites
            - 5: outlines sprites

        :param sprite: sprite to add in the draw mechanism
        :type sprite: object
        :param outlines: enable outlines
        :type outlines: bool
        :param layer: layer indice
        :type layer: int
        """
        if layer == 0 and isinstance(sprite, ArrowSprite):
            layer = 4
        elif layer == 0 and isinstance(sprite, ImageSprite):
            layer = 2
        elif layer == 0 and isinstance(sprite, TextSprite):
            layer = 1
        self.sprites.add(sprite, layer=layer)
        if outlines:
            self.sprites.add(OutlinesSprite(sprite), layer=5)

    @ property
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
            BasePygameScene.BACKGROUND = ImageSprite(size=size)
            self.sprites.add(BasePygameScene.BACKGROUND, layer=0)
        self.background.set_rect(0, 0, size[0], size[1])
        self.background.set_skin(color_or_path)
        self.background.set_crop()
        self.background.render()
        self.sprites.clear(None, self.background.image)

    def set_outlines(self, enable=True):
        """Draw outlines for each rectangle available for drawing
        images and texts.

        :param enable: enable / disable outlines
        :type enable: bool
        """
        for sprite in self.sprites.get_sprites_from_layer(5):
            if enable:
                sprite.show()
            else:
                sprite.hide()

    def set_image(self, image=None):
        """Set an image to the main place or hide it.
        """
        if image:
            self.image.set_skin(image)
            self.image.render()
            self.image.show()
        else:
            self.image.hide()

    def set_arrows(self, location, offset):
        """Set arrows attributes.
        """
        for sprite in self.sprites.get_sprites_from_layer(4):
            sprite.set_location(location)
            sprite.set_offset(offset)

    def set_text_color(self, color):
        for sprite in self.sprites.get_sprites_from_layer(1):
            sprite.set_color(color)
        for sprite in self.sprites.get_sprites_from_layer(2):
            sprite.set_color(color)
        for sprite in self.sprites.get_sprites_from_layer(4):
            sprite.set_color(color)

    def set_print_number(self, current_nbr=None, failure=False):
        pass

    def _compute_position_and_size(self, events):
        pass

    def update(self, events):
        """Pygame events processing callback method.

        :param events: list of events to process.
        :type events: list
        """
        self._compute_position_and_size(events)
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
