# -*- coding: utf-8 -*-

import os.path as osp
import PIL
import pygame

from pibooth import pictures
from pibooth import evts
from pibooth.utils import PollingTimer, LOGGER
from pibooth.view.base import BaseScene


class OutlinesSprite(pygame.sprite.DirtySprite):
    """Outlines Sprite. Paint a colored rectange around the given
    sprite.
    """

    def __init__(self, sprite, color=(255, 0, 0)):
        """
        :param sprite: sprite on which outlines are drawn
        :type sprite: object
        :param color: RGB color tuple for the outlines
        :type color: tuple
        """
        super().__init__()
        self.image = pygame.Surface((10, 10), pygame.SRCALPHA, 32)
        self.rect = sprite.rect
        self.color = color
        self.visible = 0
        self._sp = sprite
        self._sp.outlines = self
        self.enabled = True

    def __repr__(self):
        return f"{self.__class__.__name__}(rect={tuple(self.rect)}"

    def set_pressed(self, state):
        """Outline can not be pressed.
        """
        del state

    def enable(self):
        """Show outlines (only if reference sprite is visible).
        """
        self.enabled = True
        if self._sp.visible and not self.visible:
            self.visible = 1

    def disable(self):
        """Hide outlines.
        """
        self.enabled = False
        if self.visible:
            self.visible = 0

    def update(self, events):
        """Draw outlines only if visible.
        """
        if self._sp.dirty and self.visible:
            self.dirty = 1
            self.image = pygame.Surface(self.rect.size, pygame.SRCALPHA, 32)
            pygame.draw.rect(self.image, self.color, (0, 0, self.rect.width, self.rect.height), 2)


class BaseSprite(pygame.sprite.DirtySprite):

    """Base sprite for any graphical element. It handles common attributes
    and methods:
      - display: manage when sprite is displayed
      - color: manage color rendering
      - resizing: manage pygame.Rect dimension
      - outline: manage a colored rectangle around the sprite
      - event: manage pressed action
    """

    def __init__(self, size):
        super().__init__()
        self.image = None
        self.rect = pygame.Rect((0, 0), size)
        self.color = None
        self.outlines = None  # Dynamically set by outlines sprite class
        self.pressed = 0
        self.on_pressed = None
        self.toggle_timer = PollingTimer(start=False)

    def show(self):
        """Show image.
        """
        if not self.visible:
            self.visible = 1
            if self.outlines and self.outlines.enabled and not self.outlines.visible:
                self.outlines.visible = 1

    def hide(self):
        """Hide image.
        """
        if self.visible:
            self.visible = 0
            if self.outlines and self.outlines.visible:
                self.outlines.visible = 0

    def set_rect(self, x, y, width, height):
        """Set the sprite absolute position and size.

        :param x: position x
        :type x: int
        :param y: position y
        :type y: int
        :param width: background width
        :type width: int
        :param height: background height
        :type height: int
        """
        if self.rect.topleft != (int(x), int(y)):
            self.rect.topleft = (x, y)
            self.dirty = 1
        if self.rect.size != (int(width), int(height)):
            self.rect.size = (width, height)
            self.image = None  # Force rendering
            self.dirty = 1

    def set_color(self, color):
        """Re-colorize the skin.

        :param color: RGB color tuple
        :type color: tuple
        """
        if color != self.color:
            self.color = color
            self.image = None  # Force rendering
            self.dirty = 1

    def get_color(self, factor=1):
        """Return image main color.

        :param factor: more or less dark, should be > 0 and < 1
        :type factor: int
        """
        if self.color:
            return tuple(min(int(c * abs(factor)), 255) for c in self.color)
        else:
            return pygame.transform.average_color(self.image)

    def set_pressed(self, state, toggle_timeout=None):
        """Set the pressed state (1 for pressed 0 for released)
        and redraws it.

        :param state: new sprite state.
        :type state: bool.
        :param toggle_timeout: timeout after which state is toggled.
        :type toggle_timeout: int.
        """
        if self.pressed != int(state):
            self.pressed = int(state)
            if toggle_timeout:
                self.toggle_timer.start(toggle_timeout)
            if self.on_pressed is not None:
                if self.pressed and self.visible:
                    self.visible = 0
                elif not self.pressed and not self.visible:
                    self.visible = 1
                    # Trigger callback when press is released
                    self.on_pressed()

    def update(self, events):
        """Update pressed state if a toggle_timeout is defined.
        """
        if self.toggle_timer.is_started() and self.toggle_timer.is_timeout():
            self.toggle_timer.reset()
            self.set_pressed(not self.pressed)


class ImageSprite(BaseSprite):
    """Image Sprite. Handle transformation on a source image which can be:
     - RGB color tuple
     - path to an image
     - PIL image object
     - Pygame surface object
    """

    def __init__(self, skin=None, size=(10, 10), colorize=True):
        """
        :param skin: image file path, RGB color tuple,  PIL image or Pygame surface
        :type skin: str or tuple or object
        :param size: size tuple (width, height) of the image.
        :type size: tuple
        :param colorize: recolorize picture if a color is set.
        :type colorize: tuple
        """
        super().__init__(size)
        self.image_orig = None
        self.path = None
        self.crop = False
        self.hflip = False
        self.vflip = False
        self.angle = 0
        self.colorize = colorize
        if skin:
            self.set_skin(skin)

    def __repr__(self):
        if self.path:
            path = osp.basename(self.path)
        else:
            path = ''
        return f"{self.__class__.__name__}(path='{path}', rect={tuple(self.rect)})"

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
                self.image_orig = None
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

    def get_skin(self):
        """Return the current skin.
        """
        return self.path or self.image_orig

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

    def update(self, events):
        """Draw image if has changed and visible.
        """
        super().update(events)
        if self.image is None and self.visible:
            if self.image_orig is None:
                if self.path:
                    self.image_orig = pictures.load_pygame_image(self.path)
                else:
                    raise ValueError(f"Path to image is missing for '{self.__class__}'")

            if isinstance(self.image_orig, (tuple, list)):
                self.image = pygame.Surface(self.rect.size, pygame.SRCALPHA, 32)
                self.image.fill(self.image_orig)
            elif isinstance(self.image_orig, PIL.Image.Image):
                surface = pygame.image.frombuffer(self.image_orig.tobytes(),
                                                  self.image_orig.size, self.image_orig.mode)
                self.image = pictures.transform_pygame_image(surface, self.rect.size, hflip=self.hflip,
                                                             vflip=self.vflip, angle=self.angle, crop=self.crop,
                                                             color=self.color if self.colorize else None)
            else:
                self.image = pictures.transform_pygame_image(self.image_orig, self.rect.size, hflip=self.hflip,
                                                             vflip=self.vflip, angle=self.angle, crop=self.crop,
                                                             color=self.color if self.colorize else None)


class TextSprite(BaseSprite):

    """Text Sprite.
    """

    def __init__(self, text='', size=(10, 10)):
        """
        :param size: size tuple (width, height) of the image.
        :type size: tuple
        :param path: image file path
        :type path: str
        """
        super().__init__(size)
        self.text = text
        self.color = (255, 255, 255)
        self.align = pictures.ALIGN_CENTER
        if text is not None:
            self.set_text(text)

    def __repr__(self):
        return f"{self.__class__.__name__}(text='{self.text}', rect={tuple(self.rect)})"

    def set_text(self, text):
        """Set text.

        :param text: text to display
        :type text: str
        """
        if text != self.text:
            self.text = text
            self.image = None  # Force rendering
            self.dirty = 1

    def set_align(self, align):
        """Set text alignment.

        :param align: text to display
        :type align: str
        """
        if align != self.align:
            self.align = align
            self.image = None  # Force rendering
            self.dirty = 1

    def update(self, events):
        """Draw image if has changed and visible.
        """
        super().update(events)
        if self.image is None and self.visible:
            self.image = pictures.text_to_pygame_image(self.text, self.rect.size, self.color, self.align)


class ArrowSprite(ImageSprite):

    """Image Sprite dedicated to display an arrow on a specific
    location and with an offset.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.location = BaseScene.ARROW_BOTTOM
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

    """Image Sprite dedicated to display the left arrow.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_skin('arrow.png')

    def set_location(self, location):
        super().set_location(location)
        if location == BaseScene.ARROW_BOTTOM:
            self.set_flip(vflip=False)
            self.show()
        elif location == BaseScene.ARROW_TOP:
            self.set_flip(vflip=True)
            self.show()
        elif location == BaseScene.ARROW_TOUCH:
            self.show()
        else:
            self.hide()

    def set_rect(self, x, y, width, height):
        """Set the sprite absolute position and size.
        """
        x -= self.offset
        super().set_rect(x, y, width, height)

    def update(self, events):
        super().update(events)
        if self.visible:
            for event in events:
                if event.type == evts.EVT_BUTTON_CAPTURE:
                    self.set_pressed(1, 0.2)  # Timeout because not release event for HW buttons


class RightArrowSprite(LeftArrowSprite):

    """Image Sprite dedicated to display the right arrow.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_flip(hflip=True)

    def set_rect(self, x, y, width, height):
        """Set the sprite absolute position and size.
        """
        x += self.offset
        ArrowSprite.set_rect(self, x, y, width, height)

    def update(self, events):
        super(LeftArrowSprite, self).update(events)
        if self.visible:
            for event in events:
                if event.type == evts.EVT_BUTTON_PRINT:
                    self.set_pressed(1, 0.2)  # Timeout because not release event for HW buttons


class DotsSprite(BaseSprite):

    """Dot Sprite to count current capture.
    """

    def __init__(self, nbr_dots=4):
        super().__init__((100, 50))
        self.dots = []
        self.filled_orig = pictures.load_pygame_image('dot_filled.png')
        self.empty_orig = pictures.load_pygame_image('dot.png')
        self.current = 0
        self.total = nbr_dots

    def set_status(self, current, total):
        if self.total != total:
            self.total = total
            self.image = None  # Force rendering
            self.dirty = 1
        if self.current != current:
            self.current = current
            self.image = None  # Force rendering
            self.dirty = 1

    def update(self, events):
        super().update(events)
        if self.image is None and self.visible:
            self.image = pygame.Surface(self.rect.size, pygame.SRCALPHA, 32)
            border = 20
            side = min(self.rect.size) - 10
            empty_dot = pictures.transform_pygame_image(self.empty_orig, (side, side), color=self.color)
            filled_dot = pictures.transform_pygame_image(self.filled_orig, (side, side), color=self.color)
            x = (self.rect.width - (side * self.total + border * (self.total - 1))) // 2
            y = (self.rect.height - side) // 2
            for i in range(self.total):
                if i < self.current:
                    self.image.blit(filled_dot, (x, y))
                else:
                    self.image.blit(empty_dot, (x, y))
                x += (side + border)


class BasePygameScene(BaseScene):

    """Base class for Pygame scene. It use dirty sprite mechanism to
    save CPU usage.
    """

    BACKGROUND = None

    def __init__(self):
        self.sprites = pygame.sprite.LayeredDirty()
        self.image = ImageSprite()
        self.image.visible = 0
        self.add_sprite(self.image, layer=3)
        self.text_color = (255, 255, 255)
        self.arrow_location = BaseScene.ARROW_BOTTOM

        # On Raspberry Pi, the time to update dirty sprites is long (120-180ms
        # tested), increasing the treshold permits to avoid blitting full screen
        # at each draw() call.
        self.sprites.set_timing_threshold(200)

    def add_sprite(self, sprite, outlines=True, layer=0):
        """Declare a new sprite to draw. If layer is not defined (layer=0),
        layer is automatically assigned depending on the sprite type.

        Sprites are drawn as ordered. Six layers are defined:

            - 0: only ONE background sprite
            - 1: texts sprites
            - 2: assets sprites
            - 3: only ONE speciale image sprite
            - 4: arrows sprites
            - 5: outlines sprites

        :param sprite: sprite to add in the draw mechanism
        :type sprite: object
        :param outlines: enable outlines on sprite
        :type outlines: bool
        :param layer: layer indice
        :type layer: int
        """
        assert layer != 5, "Layer 5 is reserved for outlines, use outlines=True to enable it"
        if layer == 0 and isinstance(sprite, ArrowSprite):
            layer = 4
        elif layer == 0 and isinstance(sprite, (ImageSprite, DotsSprite)):
            layer = 2
        elif layer == 0 and isinstance(sprite, TextSprite):
            layer = 1
        elif layer == 0 or layer == 3:
            for oldsprite in self.sprites.get_sprites_from_layer(layer):
                LOGGER.debug("Remove %s sprite '%s'", "background" if layer == 0 else "main image", oldsprite)
                self.sprites.remove(oldsprite)

        self.sprites.add(sprite, layer=layer)
        if outlines:
            self.sprites.add(OutlinesSprite(sprite), layer=5)
        return sprite

    @property
    def background(self):
        return BasePygameScene.BACKGROUND

    @property
    def rect(self):
        return BasePygameScene.BACKGROUND.rect

    def set_background(self, color_or_path, size):
        """Set background sprite.

        :param color_or_path: color of path to an image
        :type color_or_path: tuple or str
        :param size: size tuple (width, height) of the image.
        :type size: tuple
        """
        if not BasePygameScene.BACKGROUND:
            BasePygameScene.BACKGROUND = ImageSprite(size=size)
        if not self.sprites.has(self.background):
            self.sprites.add(self.background, layer=0)
        self.background.set_rect(0, 0, size[0], size[1])
        self.background.set_skin(color_or_path)
        self.background.set_crop()

    def set_outlines(self, enable=True):
        """Draw outlines for each rectangle available for drawing
        images and texts.

        :param enable: enable / disable outlines
        :type enable: bool
        """
        for sprite in self.sprites.get_sprites_from_layer(5):
            if enable:
                sprite.enable()
            else:
                sprite.disable()

    def set_image(self, image=None):
        """Set an image to the main place or hide it.

        :param image: image to set (path, PIL object or pygame object)
        :type image: str or object
        """
        if image:
            self.image.show()
            self.image.set_skin(image)
        else:
            self.image.hide()

    def set_arrows(self, location, offset):
        """Set arrows attributes.

        :param location: arrow location: ARROW_HIDDEN, ARROW_BOTTOM, ARROW_TOP, ARROW_TOUCH
        :type location: str
        :param offset: x offset from current position to screen outer
        :type offset: int
        """
        self.arrow_location = location
        for sprite in self.sprites.get_sprites_from_layer(4):
            sprite.set_location(location)
            sprite.set_offset(offset)

    def set_text_color(self, color):
        """Set text font color.

        :param color: RGB color tuple for the texts
        :type color: tuple
        """
        self.text_color = color
        # Texts
        for sprite in self.sprites.get_sprites_from_layer(1):
            sprite.set_color(color)

        # Assets
        for sprite in self.sprites.get_sprites_from_layer(2):
            sprite.set_color(color)

        # Arrows
        for sprite in self.sprites.get_sprites_from_layer(4):
            sprite.set_color(color)

    def set_print_number(self, current_nbr=None, failure=False):
        pass

    def update(self, events):
        """Pygame events processing callback method.

        :param events: list of events to process.
        :type events: list
        """
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN\
                    and event.button in (1, 2, 3):
                # Don't consider the mouse wheel (button 4 & 5):
                sprite = evts.get_top_visible(self.sprites.get_sprites_at(event.pos))
                if sprite:
                    sprite.set_pressed(1)

            elif event.type == pygame.FINGERDOWN:
                display_size = pygame.display.get_surface().get_size()
                finger_pos = (event.x * display_size[0], event.y * display_size[1])
                sprite = evts.get_top_visible(self.sprites.get_sprites_at(finger_pos))
                if sprite:
                    sprite.set_pressed(1)

            elif (event.type == pygame.MOUSEBUTTONUP and event.button in (1, 2, 3))\
                    or event.type == pygame.FINGERUP:
                # Don't consider the mouse wheel (button 4 & 5):
                for sprite in self.sprites.sprites():
                    sprite.set_pressed(0)

        self.sprites.update(events)

    def draw(self, surface, force=False):
        """Draw the elements on scene.

        This method is optimized to be called at each loop of the
        main application. It uses DirtySprite to update only parts
        of the screen that need to be refreshed.

        The first call to this method will setup the "eraser" surface that
        will be used to redraw dirty parts of the screen.

        The `force` parameter shall be used if the surface has been redrawn:
        it reset the eraser and redraw all view elements.

        :param surface: surface the scene will be displayed at
        :type surface: object
        :param force: force the drawing of the entire surface (time consuming)
        :type force: bool

        :return: list of updated area
        :rtype: list
        """
        if force:
            self.sprites.repaint_rect(self.background.rect)
        return self.sprites.draw(surface)
