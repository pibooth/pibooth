# -*- coding: utf-8 -*-

from pibooth import pictures


class Background(object):

    def __init__(self, image_name):
        self.rect = None
        self.image_name = image_name
        self.background = None

    def __str__(self):
        """Return background final name.
        """
        return self.image_name

    def resize(self, screen):
        """Resize objects to fit to the screen.
        """
        if self.rect != screen.get_rect():
            self.rect = screen.get_rect()
            self.background = pictures.get_image(self.image_name, (self.rect.width, self.rect.height))
            return True
        return False

    def paint(self, screen):
        """Paint and animate the surfaces on the screen.
        """
        screen.fill((0, 0, 0))  # Clear background
        screen.blit(self.background, self.background.get_rect(center=self.rect.center))


class IntroBackground(Background):

    def __init__(self):
        Background.__init__(self, "intro.png")


class IntroWithPrintBackground(Background):

    def __init__(self):
        Background.__init__(self, "intro_with_print.png")


class ChooseBackground(Background):

    def __init__(self, choices):
        Background.__init__(self, "choose.png")
        self.choices = choices
        self.layout0 = None
        self.layout0_pos = None
        self.layout1 = None
        self.layout1_pos = None

    def resize(self, screen):
        if Background.resize(self, screen):
            size = (self.background.get_rect().width * 0.6, self.background.get_rect().height * 0.6)
            self.layout0 = pictures.get_image("layout{}.png".format(self.choices[0]), size)
            self.layout1 = pictures.get_image("layout{}.png".format(self.choices[1]), size)

            hinter = (self.rect.width - self.layout0.get_rect().width - self.layout1.get_rect().width) // 3
            vinter = int(self.background.get_rect(center=self.rect.center).top +
                         self.layout0.get_rect(center=self.background.get_rect().center).top * 1.3)

            self.layout0_pos = (hinter, vinter)
            self.layout1_pos = (hinter * 2 + self.layout0.get_rect().width, vinter)
            return True
        return False

    def paint(self, screen):
        Background.paint(self, screen)
        screen.blit(self.layout0, self.layout0_pos)
        screen.blit(self.layout1, self.layout1_pos)


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
            size = (self.background.get_rect().width * 0.6, self.background.get_rect().height * 0.6)

            self.layout = pictures.get_image("layout{}.png".format(self.selected), size)

            hinter = self.layout.get_rect(center=self.rect.center).left
            vinter = int(self.background.get_rect(center=self.rect.center).top +
                         self.layout.get_rect(center=self.background.get_rect().center).top * 1.3)

            self.layout_pos = (hinter, vinter)
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

    def __init__(self):
        Background.__init__(self, "print.png")


class FinishedBackground(Background):

    def __init__(self):
        Background.__init__(self, "finished.png")


class OopsBackground(Background):

    def __init__(self):
        Background.__init__(self, "oops.png")
