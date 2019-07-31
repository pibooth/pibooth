# -*- coding: utf-8 -*-

from pibooth import pictures


ARROW_TOP = 'top'
ARROW_BOTTOM = 'bottom'
ARROW_HIDDEN = 'hidden'


class Background(object):

    def __init__(self, image_name):
        self._rect = None
        self.image_name = image_name
        self.background = None

    def __str__(self):
        """Return background final name.
        """
        return self.image_name

    def get_rect(self):
        """Return the Rect object of the background image. As aspect ratio
        is kept, the size of the background may be different from the
        screen size.
        """
        return self.background.get_rect(center=self._rect.center)

    def resize(self, screen):
        """Resize objects to fit to the screen.
        """
        if self._rect != screen.get_rect():
            self._rect = screen.get_rect()
            self.background = pictures.get_image(self.image_name, (self._rect.width, self._rect.height))
            return True
        return False

    def paint(self, screen):
        """Paint and animate the surfaces on the screen.
        """
        screen.fill((0, 0, 0))  # Clear background
        screen.blit(self.background, self.get_rect())


class IntroBackground(Background):

    def __init__(self, arrow_location=ARROW_BOTTOM, arrow_offset=0):
        Background.__init__(self, "intro.png")
        self.arrow_location = arrow_location
        self.arrow_offset = arrow_offset
        self.left_arrow = None
        self.left_arrow_pos = None

    def resize(self, screen):
        if Background.resize(self, screen):
            if self.arrow_location != ARROW_HIDDEN:
                size = (self.get_rect().width * 0.3, self.get_rect().height * 0.3)

                vflip = True if self.arrow_location == ARROW_TOP else False
                self.left_arrow = pictures.get_image("arrow.png", size, vflip=vflip)

                x = int(self.get_rect().left + self.get_rect().width // 4
                        - self.left_arrow.get_rect().width // 2)
                if self.arrow_location == ARROW_TOP:
                    y = self.get_rect().top + 10
                else:
                    y = int(self.get_rect().top + 2 * self.get_rect().height // 3)

                self.left_arrow_pos = (x - self.arrow_offset, y)
            return True
        return False

    def paint(self, screen):
        Background.paint(self, screen)
        if self.arrow_location != ARROW_HIDDEN:
            screen.blit(self.left_arrow, self.left_arrow_pos)


class IntroWithPrintBackground(IntroBackground):

    def __init__(self, arrow_location=ARROW_BOTTOM, arrow_offset=0):
        IntroBackground.__init__(self, arrow_location, arrow_offset)
        self.image_name = "intro_with_print.png"


class ChooseBackground(Background):

    def __init__(self, choices, arrow_location=ARROW_BOTTOM, arrow_offset=0):
        Background.__init__(self, "choose.png")
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
        if Background.resize(self, screen):
            size = (self.get_rect().width * 0.6, self.get_rect().height * 0.6)
            self.layout0 = pictures.get_image("layout{}.png".format(self.choices[0]), size)
            self.layout1 = pictures.get_image("layout{}.png".format(self.choices[1]), size)

            inter = (self.get_rect().width - 2 * self.layout0.get_rect().width) // 3

            x0 = int(self.get_rect().left + inter)
            x1 = int(self.get_rect().left + 2 * inter + self.layout0.get_rect().width)
            y = int(self.get_rect().top + self.get_rect().height * 0.3)

            self.layout0_pos = (x0, y)
            self.layout1_pos = (x1, y)

            if self.arrow_location != ARROW_HIDDEN:
                if self.arrow_location == ARROW_TOP:
                    y = self.get_rect().top + 5
                    x_offset = 30
                    size = (self.get_rect().width * 0.1, self.layout0_pos[1] - y - 10)
                else:
                    x_offset = 0
                    y = self.layout0_pos[1] + self.layout0.get_rect().height + 5
                    size = (self.get_rect().width * 0.1, self.get_rect().bottom - y - 5)

                vflip = True if self.arrow_location == ARROW_TOP else False
                self.left_arrow = pictures.get_image("arrow.png", size, vflip=vflip)
                self.right_arrow = pictures.get_image("arrow.png", size, hflip=True, vflip=vflip)

                inter = (self.get_rect().width - 2 * self.left_arrow.get_rect().width) // 4

                x0 = int(self.get_rect().left + inter) - x_offset
                x1 = int(self.get_rect().left + 3 * inter + self.left_arrow.get_rect().width) + x_offset

                self.left_arrow_pos = (x0 - self.arrow_offset, y)
                self.right_arrow_pos = (x1 + self.arrow_offset, y)

            return True
        return False

    def paint(self, screen):
        Background.paint(self, screen)
        screen.blit(self.layout0, self.layout0_pos)
        screen.blit(self.layout1, self.layout1_pos)
        if self.arrow_location != ARROW_HIDDEN:
            screen.blit(self.left_arrow, self.left_arrow_pos)
            screen.blit(self.right_arrow, self.right_arrow_pos)


class ChosenBackground(Background):

    def __init__(self, choices, selected):
        Background.__init__(self, "chosen.png")
        self.choices = choices
        self.selected = selected
        self.layout = None
        self.layout_pos = None

    def __str__(self):
        return "chosen{}.png".format(self.selected)

    def resize(self, screen):
        if Background.resize(self, screen):
            size = (self.get_rect().width * 0.6, self.get_rect().height * 0.6)

            self.layout = pictures.get_image("layout{}.png".format(self.selected), size)

            x = self.layout.get_rect(center=self.get_rect().center).left
            y = int(self.get_rect().top + self.get_rect().height * 0.3)

            self.layout_pos = (x, y)
            return True
        return False

    def paint(self, screen):
        Background.paint(self, screen)
        screen.blit(self.layout, self.layout_pos)


class CaptureBackground(Background):

    def __init__(self):
        Background.__init__(self, "capture.png")


class ProcessingBackground(Background):

    def __init__(self):
        Background.__init__(self, "processing.png")


class PrintBackground(Background):

    def __init__(self, arrow_location=ARROW_BOTTOM, arrow_offset=0):
        Background.__init__(self, "print.png")
        self.arrow_location = arrow_location
        self.arrow_offset = arrow_offset
        self.right_arrow = None
        self.right_arrow_pos = None

    def resize(self, screen):
        if Background.resize(self, screen):
            if self.arrow_location != ARROW_HIDDEN:
                size = (self.get_rect().width * 0.3, self.get_rect().height * 0.3)

                vflip = True if self.arrow_location == ARROW_TOP else False
                self.right_arrow = pictures.get_image("arrow.png", size, hflip=True, vflip=vflip)

                x = int(self.get_rect().left + self.get_rect().width * 0.75
                        - self.right_arrow.get_rect().width // 2)

                if self.arrow_location == ARROW_TOP:
                    y = self.get_rect().top + 10
                else:
                    y = int(self.get_rect().top + 2 * self.get_rect().height // 3)

                self.right_arrow_pos = (x + self.arrow_offset, y)
            return True
        return False

    def paint(self, screen):
        Background.paint(self, screen)
        if self.arrow_location != ARROW_HIDDEN:
            screen.blit(self.right_arrow, self.right_arrow_pos)


class FinishedBackground(Background):

    def __init__(self):
        Background.__init__(self, "finished.png")


class OopsBackground(Background):

    def __init__(self):
        Background.__init__(self, "oops.png")
