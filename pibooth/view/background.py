# -*- coding: utf-8 -*-

import os.path as osp

from pibooth import fonts
from pibooth import pictures

from pibooth.fonts import get_pygame_font
from pibooth.language import get_translated_text

ARROW_TOP = 'top'
ARROW_BOTTOM = 'bottom'
ARROW_HIDDEN = 'hidden'


class Background(object):

    def __init__(self, image_name, color=(0, 0, 0), text_color=(255, 255, 255), invert=False):
        self._rect = None
        self._name = image_name
        self._need_update = False

        self._background = None
        self._background_color = color
        self._background_image = None
        self._invert = invert

        self._overlay = None

        self._texts = []  # List of (surface, rect)
        self._text_color = text_color

    def __str__(self):
        """Return background final name.
        It is used in the main window to distinguish background in the cache.
        """
        return "{}({})".format(self.__class__.__name__, self._name)

    def set_color(self, color_or_path):
        """Set background color (RGB tuple) or path to an image that used to
        fill the background.

        :param color_or_path: RGB color tuple or image path
        :type color_or_path: tuple or str
        """
        if isinstance(color_or_path, (tuple, list)):
            assert len(color_or_path) == 3, "Length of 3 is required for RGB tuple"
            if color_or_path != self._background_color:
                self._background_color = color_or_path
                self._need_update = True
        else:
            assert osp.isfile(color_or_path), "Invalid image for window background: '{}'".format(color_or_path)
            if color_or_path != self._background_image:
                self._background_image = color_or_path
                self._need_update = True

    def set_text_color(self, color):
        """Set text color (RGB tuple) used to write the texts.

        :param color: RGB color tuple
        :type color: tuple
        """
        assert len(color) == 3, "Length of 3 is required for RGB tuple"
        if color != self._text_color:
            self._text_color = color
            self._need_update = True

    def set_inverted_colors(self, invert):
        """Set invert parameter used for all images in the window.

        :param invert: value of the inversion
        :type invert: bool
        """
        if invert != self._invert:
            self._invert = invert
            self._need_update = True

    def resize(self, screen):
        """Resize objects to fit to the screen.
        """
        if self._rect != screen.get_rect():
            self._rect = screen.get_rect()

            overlay_name = "{}.png".format(self._name)
            if osp.isfile(pictures.get_filename(overlay_name)):
                self._overlay = pictures.get_pygame_image(
                    pictures.get_filename(overlay_name), (self._rect.width, self._rect.height), invert=self._invert)

            if self._background_image:
                self._background = pictures.get_pygame_image(
                    self._background_image, (self._rect.width, self._rect.height), crop=True)

            self.write_text()

            self._need_update = True

    def paint(self, screen):
        """Paint and animate the surfaces on the screen.
        """
        if self._background:
            screen.blit(self._background, (0, 0))
        else:
            screen.fill(self._background_color)
        if self._overlay:
            screen.blit(self._overlay, self._overlay.get_rect(center=self._rect.center))
        for text_surface, pos in self._texts:
            screen.blit(text_surface, pos)
        self._need_update = False

    def write_text(self, pos=None):
        """Update text surfaces
        """
        self._texts = []
        text = get_translated_text(self._name)
        if text:
            if not pos:
                pos = self._rect.center
            rect_x = 0.9 * min(2 * pos[0], 2 * (self._rect.width - pos[0]))
            rect_y = 0.9 * min(2 * pos[1], 2 * (self._rect.height - pos[1]))
            text_font = get_pygame_font(text, fonts.CURRENT, rect_x, rect_y)
            surface = text_font.render(text, True, self._text_color)
            self._texts.append((surface, surface.get_rect(center=pos)))


class IntroBackground(Background):

    def __init__(self, arrow_location=ARROW_BOTTOM, arrow_offset=0):
        Background.__init__(self, "intro")
        self.arrow_location = arrow_location
        self.arrow_offset = arrow_offset
        self.left_arrow = None
        self.left_arrow_pos = None

    def resize(self, screen):
        Background.resize(self, screen)
        if self._need_update and self.arrow_location != ARROW_HIDDEN:
            size = (self._rect.width * 0.3, self._rect.height * 0.3)

            vflip = True if self.arrow_location == ARROW_TOP else False
            self.left_arrow = pictures.get_pygame_image("arrow.png", size, vflip=vflip, invert=self._invert)

            x = int(self._rect.left + self._rect.width // 4
                    - self.left_arrow.get_rect().width // 2)
            if self.arrow_location == ARROW_TOP:
                y = self._rect.top + 10
            else:
                y = int(self._rect.top + 2 * self._rect.height // 3)

            self.left_arrow_pos = (x - self.arrow_offset, y)

    def paint(self, screen):
        Background.paint(self, screen)
        if self.arrow_location != ARROW_HIDDEN:
            screen.blit(self.left_arrow, self.left_arrow_pos)

    def write_text(self):
        """Update text surfaces
        """
        pos = (self._rect.centerx / 2, self._rect.centery)
        Background.write_text(self, pos)


class IntroWithPrintBackground(IntroBackground):

    def __init__(self, arrow_location=ARROW_BOTTOM, arrow_offset=0):
        IntroBackground.__init__(self, arrow_location, arrow_offset)
        self.right_arrow = None
        self.right_arrow_pos = None

    def __str__(self):
        """Return background final name.
        It is used in the main window to distinguish background in the cache.
        """
        return "{}({})".format(self.__class__.__name__, "intro_print")

    def resize(self, screen):
        IntroBackground.resize(self, screen)
        if self._need_update and self.arrow_location != ARROW_HIDDEN:
            size = (self._rect.width * 0.1, self._rect.height * 0.1)
            vflip = True if self.arrow_location == ARROW_TOP else False
            angle = -70 if self.arrow_location == ARROW_TOP else 70
            self.right_arrow = pictures.get_pygame_image(
                "arrow.png", size, hflip=False, vflip=vflip, angle=angle, invert=self._invert)
            x = int(self._rect.left + self._rect.width // 2
                    - self.right_arrow.get_rect().width // 2)
            if self.arrow_location == ARROW_TOP:
                y = self._rect.top + 10
            else:
                y = int(self._rect.bottom - self.right_arrow.get_rect().height * 1.1)
            self.right_arrow_pos = (x - self.arrow_offset, y)

    def paint(self, screen):
        IntroBackground.paint(self, screen)
        if self.arrow_location != ARROW_HIDDEN:
            screen.blit(self.right_arrow, self.right_arrow_pos)

    def write_text(self):
        """Update text surfaces
        """
        IntroBackground.write_text(self)
        text_size = 20 * self._rect.height // 400
        text_font = pictures.pygame.font.Font(fonts.CURRENT, text_size)
        text_strings = get_translated_text("intro_print").splitlines()
        delta_y = 0
        if self.arrow_location == ARROW_BOTTOM:
            text_strings = reversed(text_strings)
        for text_string in text_strings:
            surface = text_font.render(text_string, True, self._text_color)
            if self.arrow_location == ARROW_BOTTOM:
                pos_y = self._rect.height * 87 / 100 - delta_y
            else:
                pos_y = self._rect.height * 13 / 100 + delta_y
            pos = (self._rect.width * 45 / 100, pos_y)
            self._texts.append((surface, surface.get_rect(center=pos)))
            delta_y += surface.get_height()


class ChooseBackground(Background):

    def __init__(self, choices, arrow_location=ARROW_BOTTOM, arrow_offset=0):
        Background.__init__(self, "choose")
        self.arrow_location = arrow_location
        self.arrow_offset = arrow_offset
        self.choices = choices
        self.layout0 = None
        self.layout0_pos = None
        self.layout1 = None
        self.layout1_pos = None
        self.left_arrow = None
        self.left_arrow_pos = None
        self.right_arrow = None
        self.right_arrow_pos = None

    def resize(self, screen):
        Background.resize(self, screen)
        if self._need_update:
            size = (self._rect.width * 0.6, self._rect.height * 0.6)
            self.layout0 = pictures.get_layout_image((0, 0, 0), self.choices[0], size, invert=self._invert)
            self.layout1 = pictures.get_layout_image((0, 0, 0), self.choices[1], size, invert=self._invert)

            inter = (self._rect.width - 2 * self.layout0.get_rect().width) // 3

            x0 = int(self._rect.left + inter)
            x1 = int(self._rect.left + 2 * inter + self.layout0.get_rect().width)
            y = int(self._rect.top + self._rect.height * 0.3)

            self.layout0_pos = (x0, y)
            self.layout1_pos = (x1, y)

            if self.arrow_location != ARROW_HIDDEN:
                if self.arrow_location == ARROW_TOP:
                    y = 5
                    x_offset = 30
                    size = (self._rect.width * 0.1, self._rect.top + y + 30)
                else:
                    x_offset = 0
                    y = self.layout0_pos[1] + self.layout0.get_rect().height + 5
                    size = (self._rect.width * 0.1, self._rect.bottom - y - 5)

                vflip = True if self.arrow_location == ARROW_TOP else False
                self.left_arrow = pictures.get_pygame_image("arrow.png", size, vflip=vflip, invert=self._invert)
                self.right_arrow = pictures.get_pygame_image(
                    "arrow.png", size, hflip=True, vflip=vflip, invert=self._invert)

                inter = (self._rect.width - 2 * self.left_arrow.get_rect().width) // 4

                x0 = int(self._rect.left + inter) - x_offset
                x1 = int(self._rect.left + 3 * inter + self.left_arrow.get_rect().width) + x_offset

                self.left_arrow_pos = (x0 - self.arrow_offset, y)
                self.right_arrow_pos = (x1 + self.arrow_offset, y)

    def paint(self, screen):
        Background.paint(self, screen)
        screen.blit(self.layout0, self.layout0_pos)
        screen.blit(self.layout1, self.layout1_pos)
        if self.arrow_location != ARROW_HIDDEN:
            screen.blit(self.left_arrow, self.left_arrow_pos)
            screen.blit(self.right_arrow, self.right_arrow_pos)

    def write_text(self):
        """Update text surfaces
        """
        pos = (self._rect.centerx, self._rect.height / 8)
        Background.write_text(self, pos)


class ChosenBackground(Background):

    def __init__(self, choices, selected):
        Background.__init__(self, "chosen")
        self.choices = choices
        self.selected = selected
        self.layout = None
        self.layout_pos = None

    def __str__(self):
        """Return background final name.
        It is used in the main window to distinguish background in the cache.
        """
        return "{}({}{})".format(self.__class__.__name__, self._name, self.selected)

    def resize(self, screen):
        Background.resize(self, screen)
        if self._need_update:
            size = (self._rect.width * 0.6, self._rect.height * 0.6)

            self.layout = pictures.get_layout_image((0, 0, 0), self.selected, size, invert=self._invert)

            x = self.layout.get_rect(center=self._rect.center).left
            y = int(self._rect.top + self._rect.height * 0.3)

            self.layout_pos = (x, y)

    def paint(self, screen):
        Background.paint(self, screen)
        screen.blit(self.layout, self.layout_pos)

    def write_text(self):
        """Update text surfaces
        """
        pos = (self._rect.centerx, self._rect.height / 8)
        Background.write_text(self, pos)


class CaptureBackground(Background):

    def __init__(self):
        Background.__init__(self, "capture")


class ProcessingBackground(Background):

    def __init__(self):
        Background.__init__(self, "processing")

    def write_text(self):
        """Update text surfaces
        """
        pos = (self._rect.centerx, self._rect.height * 5 / 6)
        Background.write_text(self, pos)


class PrintBackground(Background):

    def __init__(self, arrow_location=ARROW_BOTTOM, arrow_offset=0):
        Background.__init__(self, "print")
        self.arrow_location = arrow_location
        self.arrow_offset = arrow_offset
        self.right_arrow = None
        self.right_arrow_pos = None

    def resize(self, screen):
        Background.resize(self, screen)
        if self._need_update and self.arrow_location != ARROW_HIDDEN:
            size = (self._rect.width * 0.3, self._rect.height * 0.3)

            vflip = True if self.arrow_location == ARROW_TOP else False
            self.right_arrow = pictures.get_pygame_image(
                "arrow.png", size, hflip=True, vflip=vflip, invert=self._invert)

            x = int(self._rect.left + self._rect.width * 0.75
                    - self.right_arrow.get_rect().width // 2)

            if self.arrow_location == ARROW_TOP:
                y = self._rect.top + 10
            else:
                y = int(self._rect.top + 2 * self._rect.height // 3)

            self.right_arrow_pos = (x + self.arrow_offset, y)

    def paint(self, screen):
        Background.paint(self, screen)
        if self.arrow_location != ARROW_HIDDEN:
            screen.blit(self.right_arrow, self.right_arrow_pos)

    def write_text(self):
        """Update text surfaces
        """
        pos = (self._rect.centerx * 3 / 2, self._rect.centery)
        Background.write_text(self, pos)


class FinishedBackground(Background):

    def __init__(self):
        Background.__init__(self, "finished")

    def write_text(self):
        """Update text surfaces
        """
        pos = (self._rect.centerx, self._rect.height * 4 / 5)
        Background.write_text(self, pos)


class OopsBackground(Background):

    def __init__(self):
        Background.__init__(self, "oops")
