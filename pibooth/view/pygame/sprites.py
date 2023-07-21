# -*- coding: utf-8 -*-

import os.path as osp
import PIL
import pygame
from pygame import gfxdraw
import numpy as np

from pibooth import pictures
from pibooth import evts
from pibooth import fonts
from pibooth.utils import PollingTimer
from pibooth.view.base import BaseScene


class OptimizedLayeredDirty(pygame.sprite.LayeredDirty):

    @staticmethod
    def _find_dirty_area(_clip, _old_rect, _rect, _sprites, _update, _update_append, init_rect):
        for spr in _sprites:
            if spr.dirty > 0:
                # Check if the sprite is obscured by sprites from higher layers
                visible = True
                for other_spr in _sprites:
                    if (other_spr is not spr
                        and other_spr.layer > spr.layer
                        and other_spr.rect.colliderect(spr.rect)):
                        # Check the visibility and transparency of the sprite
                        if spr.visible and hasattr(spr, "image") and hasattr(spr.image, "convert_alpha"):
                            pixel_array = pygame.surfarray.array_alpha(spr.image)
                            if np.any(pixel_array < 255):  # Check if there are transparent pixels
                                # Update the lower layers
                                lower_layers = [
                                    s for s in _sprites if s.layer < spr.layer
                                ]
                                for lower_spr in lower_layers:
                                    # Check if the sprite in the lower layers is visible before marking it as "dirty"
                                    if lower_spr.rect.colliderect(spr.rect) and lower_spr.visible:
                                        lower_spr.dirty = 1
                                        # You can also perform other actions here
                                visible = False
                        break

                if visible:
                    # Choose the correct rectangle (_union_rect) based on the sprite's source_rect or sprite's rect.
                    if spr.source_rect:
                        _union_rect = _rect(spr.rect.topleft, spr.source_rect.size)
                    else:
                        _union_rect = _rect(spr.rect)

                    # ... (the rest of the code remains unchanged)
                    # Add the merged rectangle to _update after applying the clip to respect the screen boundaries.
                    _update_append(_union_rect.clip(_clip))

                    # Check the old rectangles (if the sprite had an old rectangle).
                    if _old_rect[spr] is not init_rect:
                        _union_rect = _rect(_old_rect[spr])
                        # ... (the rest of the code remains unchanged)
                        # Add the merged rectangle (from the sprite's old rectangle) to _update after applying the clip.
                        _update_append(_union_rect.clip(_clip))


class BaseSprite(pygame.sprite.DirtySprite):

    """Base sprite for any graphical element. It handles common attributes
    and methods:
      - show/hide: manage when sprite is displayed
      - color: manage color rendering
      - resizing: manage pygame.Rect dimension
      - outline: manage a colored rectangle around the sprite
      - event: manage pressed action

    A sprite can be composed it-self with other sprites (called sub-sprites).
    For instance, the outlines are sub-sprites.
    """

    def __init__(self, parent=None, size=(10, 10), outlines=True, layer=None):
        """
        :param parent: sprite on which outlines are drawn
        :type parent: object
        :param size: size tuple (width, height) of the image
        :type size: tuple
        :param outlines: enable oulines on current rect sprite
        :type outlines: bool
        :param layer: layer number used to order draw actions
        :type layer: int
        """
        super().__init__()
        assert parent is None or isinstance(parent, (BasePygameScene, BaseSprite))
        self._image_cache = None
        self._subsprites = []  # Sub-sprites composing the sprite
        self.parent = parent
        self.rect = pygame.Rect((0, 0), size)
        self.color = None
        self.pressed = 0
        self.on_pressed = None
        self.toggle_timer = PollingTimer(start=False)
        self.layer = layer
        if self.parent:
            self.parent.add_sprite(self)
        if outlines:
            self.add_sprite(OutlinesSprite(self))

    def get_sprites(self, include_outlines=True, recursive=False):
        """Return all sub-sprites.
        """
        if recursive:
            sprites = []
            sprites.extend(self._subsprites)
            for sprite in self._subsprites:
                sprites += sprite.get_sprites(include_outlines, recursive)
            return sprites
        elif not include_outlines:
            return [sprite for sprite in self._subsprites if not isinstance(sprite, OutlinesSprite)]
        else:
            return self._subsprites

    def draw(self):
        """Render sprite image.

        :return: image for the sprite
        :rtype: Pygame surface
        """
        raise NotImplementedError

    @property
    def image(self):
        """Return current sprite image.
        """
        if not self._image_cache:
            self._image_cache = self.draw()
        return self._image_cache

    def set_dirty(self, redraw=True):
        """Declare that the sprite has changed (at least its position).

        :param redraw: if True, the sprite image is redrawn
        """
        self.dirty = 1
        if redraw:
            self._image_cache = None
        for sprite in self.get_sprites():
            if isinstance(sprite, OutlinesSprite):
                sprite.set_dirty(redraw)

    def add_sprite(self, sprite):
        """Add a sub-sprite to compose the sprite.
        """
        assert isinstance(sprite, BaseSprite), f"Sub-sprite '{sprite}' shall inherite from 'BaseSprite' class"
        if sprite.parent == self:
            # Register direct sprites
            self._subsprites.append(sprite)
        if self.parent:
            # Propagate to parent
            self.parent.add_sprite(sprite)
        return sprite

    def show(self):
        """Show sprite.
        """
        if not self.visible:
            self.visible = 1
            for sprite in self.get_sprites():
                sprite.show()

    def hide(self):
        """Hide sprite.
        """
        if self.visible:
            self.visible = 0
            for sprite in self.get_sprites():
                sprite.hide()

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
        assert width > 0, "Sprite width shall be greater than zero"
        assert height > 0, "Sprite height shall be greater than zero"
        if self.rect.topleft != (int(x), int(y)):
            self.rect.topleft = (x, y)
            self.set_dirty(False)
        if self.rect.size != (int(width), int(height)):
            self.rect.size = (width, height)
            self.set_dirty()

    def set_color(self, color):
        """Re-colorize the skin.

        :param color: RGB color tuple
        :type color: tuple
        """
        if color != self.color:
            self.color = color
            self.set_dirty()

    def get_color(self, factor=1):
        """Return image main color.

        :param factor: more or less dark, should be > 0 and < 1
        :type factor: int
        """
        if self.color:
            return tuple(min(int(c * abs(factor)), 255) for c in self.color)
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


class OutlinesSprite(BaseSprite):

    """Outlines Sprite. Paint a colored rectange around the given
    sprite.
    """

    def __init__(self, parent, color=(255, 0, 0)):
        """
        :param parent: sprite on which outlines are drawn
        :type parent: object
        :param color: RGB color tuple for the outlines
        :type color: tuple
        """
        super().__init__(parent, outlines=False, layer=BasePygameScene.LAYER_OUTLINES)
        self.rect = parent.rect
        self.color = color
        self.visible = 0
        self.enabled = False

    def __repr__(self):
        return f"{self.__class__.__name__}({self.parent})"

    def draw(self):
        """Render image.
        """
        image = pygame.Surface(self.rect.size, pygame.SRCALPHA, 32)
        pygame.draw.rect(image, self.color, (0, 0, self.rect.width, self.rect.height), 2)
        return image

    def show(self):
        """Show sprite.
        """
        if not self.visible and self.enabled:
            self.visible = 1

    def hide(self):
        """Hide sprite.
        """
        if self.visible:
            self.visible = 0

    def add_sprite(self, sprite):
        """Add a sub-sprite to compose the sprite.
        """
        raise ValueError(f"Adding sub-sprite {sprite} to {self.__class__.__name__} not permited")

    def set_pressed(self, state, toggle_timeout=None):
        """Outline can not be pressed.
        """
        del state, toggle_timeout

    def enable(self):
        """Show outlines (only if reference sprite is visible).
        """
        if not self.enabled:
            self.enabled = True
            if self.parent.visible and not self.visible:
                self.visible = 1

    def disable(self):
        """Hide outlines.
        """
        if self.enabled:
            self.enabled = False
            self.visible = 0


class ImageSprite(BaseSprite):

    """Image Sprite. Handle transformation on a source image which can be:
     - RGB color tuple
     - path to an image
     - PIL image object
     - Pygame surface object
    """

    def __init__(self, parent, skin=None, colorize=True, **kwargs):
        """
        :param parent: sprite to which current sprite is linked
        :type parent: object
        :param skin: image file path, RGB color tuple,  PIL image or Pygame surface
        :type skin: str or tuple or object
        :param colorize: recolorize picture if a color is set.
        :type colorize: tuple
        """
        kwargs['layer'] = kwargs.get('layer', BasePygameScene.LAYER_IMAGES)
        super().__init__(parent, **kwargs)
        self._image_orig = None
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
            elem = f"path='{osp.basename(self.path)}'"
        else:
            elem = f"image={self._image_orig}"
        return f"{self.__class__.__name__}({elem}, rect={tuple(self.rect)})"

    def draw(self):
        """Render image.
        """
        if self._image_orig is None:
            if self.path:
                self._image_orig = pictures.load_pygame_image(self.path)
            else:
                raise ValueError(f"Path to image is missing for '{self}'")

        if isinstance(self._image_orig, (tuple, list)):
            image = pygame.Surface(self.rect.size, pygame.SRCALPHA, 32)
            image.fill(self._image_orig)
            return image
        elif isinstance(self._image_orig, PIL.Image.Image):
            surface = pygame.image.frombuffer(self._image_orig.tobytes(),
                                              self._image_orig.size, self._image_orig.mode)
            return pictures.transform_pygame_image(surface, self.rect.size, hflip=self.hflip,
                                                   vflip=self.vflip, angle=self.angle, crop=self.crop,
                                                   color=self.color if self.colorize else None)
        else:
            return pictures.transform_pygame_image(self._image_orig, self.rect.size, hflip=self.hflip,
                                                   vflip=self.vflip, angle=self.angle, crop=self.crop,
                                                   color=self.color if self.colorize else None)

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
                self.path = skin
                self._image_orig = None
                self.set_dirty()
        elif isinstance(skin, (tuple, list)):
            assert len(skin) == 3, "Length of 3 is required for RGB tuple"
            if skin != self._image_orig:
                self.path = None
                self._image_orig = skin
                self.set_dirty()
        else:
            assert isinstance(skin, (PIL.Image.Image, pygame.Surface)), "PIL Image or Pygame Surface is required"
            if skin != self._image_orig:
                self.path = None
                self._image_orig = skin
                self.set_dirty()

    def get_skin(self):
        """Return the current skin.
        """
        return self.path or self._image_orig

    def set_crop(self, crop=True):
        """Crop the skin to fit sprite size.

        :param crop: crop image to fit aspect ratio of the size
        :type crop: bool
        """
        if crop != self.crop:
            self.crop = crop
            self.set_dirty()

    def set_flip(self, hflip=None, vflip=None):
        """Flip the skin vertically or horizontally.

        :param hflip: apply an horizontal flip
        :type hflip: bool
        :param vflip: apply a vertical flip
        :type vflip: bool
        """
        if hflip is not None and hflip != self.hflip:
            self.hflip = hflip
            self.set_dirty()
        if vflip is not None and vflip != self.vflip:
            self.vflip = vflip
            self.set_dirty()

    def set_angle(self, angle=0):
        """Rotate the skin.

        :param angle: angle of rotation of the image
        :type angle: int
        """
        if angle != self.angle:
            self.angle = angle
            self.set_dirty()


class TextSprite(BaseSprite):

    """Text Sprite.
    """

    def __init__(self, parent, text='', font_name=None, **kwargs):
        """
        :param parent: sprite to which current sprite is linked
        :type parent: object
        :param text: text to draw
        :type text: str
        :param font_name: font name
        :type font_name: str
        """
        kwargs['layer'] = kwargs.get('layer', BasePygameScene.LAYER_TEXTS)
        super().__init__(parent, **kwargs)
        self.text = text
        self.color = (255, 255, 255)
        self.align = fonts.ALIGN_CENTER
        self.font_name = font_name
        if text is not None:
            self.set_text(text)

    def __repr__(self):
        return f"{self.__class__.__name__}(text='{self.text}', rect={tuple(self.rect)})"

    def draw(self):
        """Render text.
        """
        return pictures.text_to_pygame_image(
            self.text, self.rect.size, self.color, self.align, font_name=self.font_name)

    def set_text(self, text):
        """Set text.

        :param text: text to display
        :type text: str
        """
        if text != self.text:
            self.text = text
            self.set_dirty()

    def set_align(self, align):
        """Set text alignment.

        :param align: text to display
        :type align: str
        """
        if align != self.align:
            self.align = align
            self.set_dirty()


class ArrowSprite(ImageSprite):

    """Image Sprite dedicated to display an arrow on a specific
    location and with an offset.
    """

    def __init__(self, *args, **kwargs):
        kwargs['layer'] = kwargs.get('layer', BasePygameScene.LAYER_ARROWS)
        super().__init__(*args, **kwargs)
        self.location = BaseScene.ARROW_BOTTOM
        self.offset = 0

    def set_location(self, location):
        if location != self.location:
            self.location = location
            self.set_dirty()

    def set_offset(self, offset):
        if offset != self.offset:
            self.offset = offset
            self.set_dirty()


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


class CapturesCounterSprite(BaseSprite):

    """CapturesCounter Sprite to display current capture number.
    """

    def __init__(self, parent, nbr_dots=4, **kwargs):
        kwargs['layer'] = kwargs.get('layer', BasePygameScene.LAYER_IMAGES)
        super().__init__(parent, **kwargs)
        self.dot_skin = pictures.load_pygame_image('dot.png')
        self.dot_checked_skin = pictures.load_pygame_image('dot_checked.png')
        self.current = 0
        self.total = nbr_dots

        for i in range(self.total):
            ImageSprite(self, skin=self.dot_skin, outlines=False)

    def set_color(self, color):
        """Set dots color.
        """
        super().set_color(color)
        for sprite in self.get_sprites(include_outlines=False):
            sprite.set_color(color)

    def draw(self):
        """Render dots.
        """
        for i, sprite in enumerate(self.get_sprites(include_outlines=False)):
            if i < self.current:
                sprite.set_skin(self.dot_checked_skin)
            else:
                sprite.set_skin(self.dot_skin)
        return pygame.Surface(self.rect.size, pygame.SRCALPHA, 32)

    def set_rect(self, x, y, width, height):
        """Update dots position.
        """
        super().set_rect(x, y, width, height)
        border = 20
        side = min(self.rect.size) - 10
        x = (self.rect.width - (side * self.total + border * (self.total - 1))) // 2
        y = (self.rect.height - side) // 2
        for sprite in self.get_sprites(include_outlines=False):
            sprite.set_rect(self.rect.x + x, self.rect.y + y, side, side)
            x += (side + border)

    def set_status(self, current, total):
        """Update counter values
        """
        if self.total != total:
            self.total = total
            for i, sprite in enumerate(self.get_sprites(include_outlines=False)):
                if i < self.total:
                    sprite.show()
                else:
                    sprite.hide()
            self.set_rect(*self.rect)  # Force recalculate dots position
        if self.current != current:
            self.current = current
            self.set_dirty()


class StatusBarSprite(BaseSprite):

    """Sprite to display the current system status (printer queue, failure, ...).
    """

    def __init__(self, parent, **kwargs):
        kwargs['layer'] = kwargs.get('layer', BasePygameScene.LAYER_STATUS)
        super().__init__(parent, **kwargs)
        self._failure = False

        self.printer_queue_nbr = TextSprite(self, '0', size=(8, 8), font_name='Monoid-Regular.ttf',
                                            outlines=False, layer=self.layer)
        self.printer_queue_icon = ImageSprite(self, 'sheet.png', size=(8, 8),
                                              outlines=False, layer=self.layer)
        self.printed_nbr = TextSprite(self, '0', size=(8, 8), font_name='Monoid-Regular.ttf',
                                      outlines=False, layer=self.layer)
        self.printer_icon = ImageSprite(self, 'printer.png', size=(8, 8),
                                        outlines=False, layer=self.layer)
        self.taken_nbr = TextSprite(self, '0', size=(8, 8), font_name='Monoid-Regular.ttf',
                                    outlines=False, layer=self.layer)
        self.captures_icon = ImageSprite(self, 'capture.png', size=(8, 8),
                                         outlines=False, layer=self.layer)

    def draw(self):
        """Render statusbar.
        """
        image = pygame.Surface(self.rect.size, pygame.SRCALPHA, 32)
        width = min(self.rect.width, self.rect.height)
        gfxdraw.aacircle(image, -1, width, width, (40, 41, 35))
        gfxdraw.filled_circle(image, -1, width, width, (40, 41, 35))
        gfxdraw.aacircle(image, -1, self.rect.height - width, width, (40, 41, 35))
        gfxdraw.filled_circle(image, -1, self.rect.height - width, width, (40, 41, 35))
        gfxdraw.box(image, (0, width, width, self.rect.height - 2 * width), (40, 41, 35))
        return image

    def set_printer_queue(self, size):
        """Set number of print in progress.
        """
        self.printer_queue_nbr.set_text(str(size))

    def set_printer_failure(self, failure=False):
        """Change printer status."""
        if self._failure != failure:  # Avoid recreate failed icon
            self._failure = failure
            if self._failure:
                skin = pictures.load_pygame_image('printer.png')
                skin.blit(pictures.load_pygame_image('action_failed.png'), (0, 0))
                self.printer_queue_icon.set_skin(skin)
            else:
                self.printer_queue_icon.set_skin('printer.png')

    def set_printed_counter(self, count):
        """Set counter.
        """
        self.printed_nbr.set_text(str(count))

    def set_taken_counter(self, count):
        """Set counter.
        """
        self.taken_nbr.set_text(str(count))

    def set_rect(self, x, y, width, height):
        """Update picto position.
        """
        super().set_rect(x, y, width, height)
        start_padding = width // 2
        icon_height = (height - 2 * start_padding) // len(self.get_sprites(include_outlines=False))
        padding = icon_height // 10
        icon_height -= padding

        y += start_padding
        for sprite in self.get_sprites(include_outlines=False):
            sprite.set_rect(x, y, width, icon_height - padding)
            y += (icon_height + padding)


class BasePygameScene(BaseScene):

    """Base class for Pygame scene. It use dirty sprite mechanism to
    save CPU usage.

    Sprites are drawn as ordered. Seven layers are defined:

        - 0: only ONE background sprite
        - 2: images sprites
        - 4: texts sprites
        - 5: only ONE speciale image sprite
        - 6: arrows sprites
        - 8: system status sprites
        - 10: outlines sprites

    The layer LAYER_PICTURE is initialized with an `ImageSprite` hidden
    by default.
    """
    LAYER_BACKGROUND = 0
    LAYER_IMAGES = 2
    LAYER_TEXTS = 4
    LAYER_PICTURE = 5
    LAYER_ARROWS = 6
    LAYER_STATUS = 8
    LAYER_OUTLINES = 10

    def __init__(self):
        self.sprites = OptimizedLayeredDirty()
        self.image = ImageSprite(self, layer=BasePygameScene.LAYER_PICTURE)
        self.image.visible = 0
        self.text_color = (255, 255, 255)
        self.arrow_location = BaseScene.ARROW_BOTTOM

        # On Raspberry Pi, the time to update dirty sprites is long (120-180ms
        # tested), increasing the treshold permits to avoid blitting full screen
        # at each draw() call.
        self.sprites.set_timing_threshold(600)

    def add_sprite(self, sprite):
        """Declare a new sprite to draw.

        :param sprite: sprite to add in the draw mechanism
        :type sprite: object
        """
        self.sprites.add(sprite)
        if not sprite.parent:
            # Parent not defined, means that sub-sprites are not registered
            self.sprites.add(*sprite.get_sprites(recursive=True))
        return sprite

    def get_top_sprite_at(self, pos, from_layers=None):
        """Return the top sprite (last of the `from_layers`) which is visible.
        If `from_layers` is not defined, only a sprite from "clickable" layers
        will be returned.

        :param pos: position (x,y)
        :type pos: tuple
        :param from_layers: layers to belong to
        :type from_layers: list
        """
        if from_layers is None:
            from_layers = (BasePygameScene.LAYER_IMAGES,
                           BasePygameScene.LAYER_TEXTS,
                           BasePygameScene.LAYER_PICTURE,
                           BasePygameScene.LAYER_ARROWS,
                           BasePygameScene.LAYER_STATUS)
        for sprite in reversed(self.sprites.get_sprites_at(pos)):
            if sprite.visible and sprite.layer in from_layers:
                return sprite
        return None

    @property
    def background(self):
        for sprite in self.sprites.get_sprites_from_layer(BasePygameScene.LAYER_BACKGROUND):
            if isinstance(sprite, ImageSprite):
                return sprite
        raise RuntimeError("Background is not initialized")

    @property
    def status_bar(self):
        for sprite in self.sprites.get_sprites_from_layer(BasePygameScene.LAYER_STATUS):
            if isinstance(sprite, StatusBarSprite):
                return sprite
        raise RuntimeError("Status bar is not initialized")

    @property
    def rect(self):
        return self.background.rect

    def set_outlines(self, enable=True):
        """Draw outlines for each rectangle available for drawing
        images and texts.

        :param enable: enable / disable outlines
        :type enable: bool
        """
        for sprite in self.sprites.get_sprites_from_layer(BasePygameScene.LAYER_OUTLINES):
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
        for sprite in self.sprites.get_sprites_from_layer(BasePygameScene.LAYER_ARROWS):
            sprite.set_location(location)
            sprite.set_offset(offset)

    def set_text_color(self, color):
        """Set text font color.

        :param color: RGB color tuple for the texts
        :type color: tuple
        """
        self.text_color = color
        # Assets
        for sprite in self.sprites.get_sprites_from_layer(BasePygameScene.LAYER_IMAGES):
            sprite.set_color(color)

        # Texts
        for sprite in self.sprites.get_sprites_from_layer(BasePygameScene.LAYER_TEXTS):
            sprite.set_color(color)

        # Arrows
        for sprite in self.sprites.get_sprites_from_layer(BasePygameScene.LAYER_ARROWS):
            sprite.set_color(color)

    def update(self, events):
        """Pygame events processing callback method.

        :param events: list of events to process.
        :type events: list
        """
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN\
                    and event.button in (1, 2, 3):
                # Don't consider the mouse wheel (button 4 & 5):
                sprite = self.get_top_sprite_at(event.pos)
                if sprite:
                    sprite.set_pressed(1)

            elif event.type == pygame.FINGERDOWN:
                display_size = pygame.display.get_surface().get_size()
                finger_pos = (event.x * display_size[0], event.y * display_size[1])
                sprite = self.get_top_sprite_at(finger_pos)
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
