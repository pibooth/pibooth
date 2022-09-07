# -*- coding: utf-8 -*-

import pygame
from pibooth.view.base import BaseWindow
from pibooth.language import get_translated_text
from pibooth.view.pygame.scenes.base import BasePygameScene, LeftArrowSprite, RightArrowSprite, TextSprite


class WaitScene(BasePygameScene):

    def __init__(self, name):
        super(WaitScene, self).__init__(name)
        self.left_arrow = LeftArrowSprite()
        self.add_sprite(self.left_arrow)
        self.right_arrow = RightArrowSprite()
        self.add_sprite(self.right_arrow)
        self.intro = TextSprite(get_translated_text("intro"))
        self.add_sprite(self.intro)
        self.intro_print = TextSprite(get_translated_text("intro_print"))
        self.add_sprite(self.intro_print)

    def _compute_position_and_size(self, events):
        # Previous picture
        self.image.set_rect(self.rect.centerx, 0, self.rect.width//2, self.rect.height)

        # Take picture text
        text_border = 20
        self.intro.set_text(get_translated_text("intro"))
        if self.arrow_location == BaseWindow.ARROW_HIDDEN:
            self.intro.set_rect(text_border, text_border,
                                self.rect.width // 2 - 2 * text_border,
                                self.rect.height - 2 * text_border)
        elif self.arrow_location == BaseWindow.ARROW_BOTTOM:
            self.intro.set_rect(text_border, text_border,
                                self.rect.width // 2 - 2 * text_border,
                                self.rect.height * 0.6 - text_border)
        elif self.arrow_location == BaseWindow.ARROW_TOUCH:
            self.intro.set_rect(text_border, text_border,
                                self.rect.width // 2 - 2 * text_border,
                                self.rect.height * 0.4 - text_border)
        else:
            self.intro.set_rect(text_border, self.rect.height * 0.4,
                                self.rect.width // 2 - 2 * text_border,
                                self.rect.height * 0.6 - text_border)

        # Print text
        self.intro_print.set_text(get_translated_text("intro_print"))
        rect = pygame.Rect(self.rect.width * 0.3, 0, self.rect.width * 0.2, self.rect.height * 0.2)
        if self.arrow_location == BaseWindow.ARROW_TOP:
            rect.top = self.rect.height * 0.08
        else:
            rect.bottom = self.rect.height - self.rect.height * 0.08
        self.intro_print.set_rect(*tuple(rect))

        # Left arrow
        if self.arrow_location == BaseWindow.ARROW_TOUCH:
            self.left_arrow.set_skin('touch.png')
            size = (self.rect.width * 0.2, self.rect.height * 0.2)
            x = self.rect.width * 0.2
            y = self.rect.height // 2
        elif self.arrow_location in [BaseWindow.ARROW_BOTTOM, BaseWindow.ARROW_TOP]:
            self.left_arrow.set_skin('arrow.png')
            size = (self.rect.width * 0.3, self.rect.height * 0.3)
            x = self.rect.left + self.rect.width // 4 - size[0] // 2
            if self.arrow_location == BaseWindow.ARROW_TOP:
                y = self.rect.top + 10
            else:
                y = self.rect.bottom - size[1] - 10
        if self.arrow_location != BaseWindow.ARROW_HIDDEN:
            self.left_arrow.set_rect(x - self.left_arrow.offset, y, size[0], size[1])

        # Right arrow
        size = (self.rect.width * 0.1, self.rect.height * 0.1)
        x = self.rect.centerx - size[0]
        if self.arrow_location == BaseWindow.ARROW_TOP:
            y = self.rect.top + 10
        else:
            y = self.rect.bottom - size[1] - 10
        if self.arrow_location == BaseWindow.ARROW_TOUCH:
            self.right_arrow.set_skin('touch_print.png')
            self.right_arrow.set_flip(hflip=False)
        elif self.arrow_location in [BaseWindow.ARROW_BOTTOM, BaseWindow.ARROW_TOP]:
            self.right_arrow.set_skin('arrow.png')
            self.right_arrow.set_angle(-60)
        if self.arrow_location != BaseWindow.ARROW_HIDDEN:
            self.right_arrow.set_rect(x + self.right_arrow.offset, y, size[0], size[1])

    def update_print_action(self, enabled=True):
        if enabled and self.right_arrow.location != BaseWindow.ARROW_HIDDEN:
            self.right_arrow.show()
        else:
            self.right_arrow.hide()
