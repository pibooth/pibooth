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

    def __init__(self, image_name, color=(0, 0, 0), text_color=(255, 255, 255)):
        self._rect = None
        self._image_name = image_name
        self._need_update = False

        self._background = None
        self._background_color = color
        self._background_image = None

        self._overlay = None
        self._overlay_image = "{0}.png".format(image_name)

        self._texts = []  # list of (surface, rect)
        self._text_color = text_color

    def __str__(self):
        """Return background final name.
        """
        return self._overlay_image

    def get_rect(self):
        """Return the Rect object of the background image. As aspect ratio
        is kept, the size of the background may be different from the
        screen size.
        """
        return self._overlay.get_rect(center=self._rect.center)

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

    def resize(self, screen):
        """Resize objects to fit to the screen.
        """
        if self._rect != screen.get_rect():
            self._rect = screen.get_rect()

            self._overlay = pictures.get_pygame_image(self._overlay_image, (self._rect.width, self._rect.height))
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
        screen.blit(self._overlay, self.get_rect())
        for text_surface, pos in self._texts:
            screen.blit(text_surface, pos)
        self._need_update = False

    def write_text(self, pos=None):
        """Update text surfaces
        """
        self._texts = []
        text = get_translated_text(self._image_name)
        if text:
            if not pos:
                pos = self._rect.center
            rect_x = 0.9*min(2*pos[0], 2*(self._rect.width - pos[0]))
            rect_y = 0.9*min(2*pos[1], 2*(self._rect.height - pos[1]))
            text_font = get_pygame_font(text, fonts.get_filename(fonts.CURRENT), rect_x, rect_y)
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
        if self._need_update:
            if self.arrow_location != ARROW_HIDDEN:
                size = (self.get_rect().width * 0.3, self.get_rect().height * 0.3)

                vflip = True if self.arrow_location == ARROW_TOP else False
                self.left_arrow = pictures.get_pygame_image("arrow.png", size, vflip=vflip)

                x = int(self.get_rect().left + self.get_rect().width // 4
                        - self.left_arrow.get_rect().width // 2)
                if self.arrow_location == ARROW_TOP:
                    y = self.get_rect().top + 10
                else:
                    y = int(self.get_rect().top + 2 * self.get_rect().height // 3)

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
        self._overlay_image = "intro_print"
        self.right_arrow = None
        self.right_arrow_pos = None

    def resize(self, screen):
        IntroBackground.resize(self, screen)
        if self._need_update and self.arrow_location != ARROW_HIDDEN:
            size = (self.get_rect().width * 0.1, self.get_rect().height * 0.1)
            vflip = True if self.arrow_location == ARROW_TOP else False
            angle = -70 if self.arrow_location == ARROW_TOP else 70
            self.right_arrow = pictures.get_pygame_image("arrow.png", size, hflip=False, vflip=vflip, angle=angle)
            x = int(self.get_rect().left + self.get_rect().width // 2
                    - self.right_arrow.get_rect().width // 2)
            if self.arrow_location == ARROW_TOP:
                y = self.get_rect().top + 10
            else:
                y = int(self.get_rect().bottom - self.right_arrow.get_rect().height*1.1)
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
        text_font = pictures.pygame.font.Font(fonts.get_filename(fonts.CURRENT), text_size)
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
            size = (self.get_rect().width * 0.6, self.get_rect().height * 0.6)
            self.layout0 = pictures.get_layout_image((0, 0, 0), self.choices[0], size)
            self.layout1 = pictures.get_layout_image((0, 0, 0), self.choices[1], size)

            inter = (self.get_rect().width - 2 * self.layout0.get_rect().width) // 3

            x0 = int(self.get_rect().left + inter)
            x1 = int(self.get_rect().left + 2 * inter + self.layout0.get_rect().width)
            y = int(self.get_rect().top + self.get_rect().height * 0.3)

            self.layout0_pos = (x0, y)
            self.layout1_pos = (x1, y)

            if self.arrow_location != ARROW_HIDDEN:
                if self.arrow_location == ARROW_TOP:
                    y = 5
                    x_offset = 30
                    size = (self.get_rect().width * 0.1, self.get_rect().top + y + 30)
                else:
                    x_offset = 0
                    y = self.layout0_pos[1] + self.layout0.get_rect().height + 5
                    size = (self.get_rect().width * 0.1, self.get_rect().bottom - y - 5)

                vflip = True if self.arrow_location == ARROW_TOP else False
                self.left_arrow = pictures.get_pygame_image("arrow.png", size, vflip=vflip)
                self.right_arrow = pictures.get_pygame_image("arrow.png", size, hflip=True, vflip=vflip)

                inter = (self.get_rect().width - 2 * self.left_arrow.get_rect().width) // 4

                x0 = int(self.get_rect().left + inter) - x_offset
                x1 = int(self.get_rect().left + 3 * inter + self.left_arrow.get_rect().width) + x_offset

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
        pos = (self._rect.centerx, self._rect.height / 7)
        Background.write_text(self, pos)


class ChosenBackground(Background):

    def __init__(self, choices, selected):
        Background.__init__(self, "chosen")
        self.choices = choices
        self.selected = selected
        self.layout = None
        self.layout_pos = None

    def __str__(self):
        return "chosen{}.png".format(self.selected)

    def resize(self, screen):
        Background.resize(self, screen)
        if self._need_update:
            size = (self.get_rect().width * 0.6, self.get_rect().height * 0.6)

            # self.layout = pictures.get_pygame_image("layout{}.png".format(self.selected), size)
            self.layout = pictures.get_layout_image((0, 0, 0), self.selected, size)

            x = self.layout.get_rect(center=self.get_rect().center).left
            y = int(self.get_rect().top + self.get_rect().height * 0.3)

            self.layout_pos = (x, y)

    def paint(self, screen):
        Background.paint(self, screen)
        screen.blit(self.layout, self.layout_pos)

    def write_text(self):
        """Update text surfaces
        """
        pos = (self._rect.centerx, self._rect.height / 7)
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
        if self._need_update:
            if self.arrow_location != ARROW_HIDDEN:
                size = (self.get_rect().width * 0.3, self.get_rect().height * 0.3)

                vflip = True if self.arrow_location == ARROW_TOP else False
                self.right_arrow = pictures.get_pygame_image("arrow.png", size, hflip=True, vflip=vflip)

                x = int(self.get_rect().left + self.get_rect().width * 0.75
                        - self.right_arrow.get_rect().width // 2)

                if self.arrow_location == ARROW_TOP:
                    y = self.get_rect().top + 10
                else:
                    y = int(self.get_rect().top + 2 * self.get_rect().height // 3)

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
