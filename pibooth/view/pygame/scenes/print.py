# -*- coding: utf-8 -*-

import pygame
from pibooth import pictures, evts
from pibooth.language import get_translated_text
from pibooth.view.pygame.sprites import BasePygameScene, LeftArrowSprite, RightArrowSprite, TextSprite


class PrintScene(BasePygameScene):

    def __init__(self, name):
        super(PrintScene, self).__init__(name)
        self.left_arrow = self.add_sprite(LeftArrowSprite())
        self.right_arrow = self.add_sprite(RightArrowSprite())
        self.text = self.add_sprite(TextSprite(get_translated_text('print')))
        self.text_print = self.add_sprite(TextSprite(get_translated_text('print_forget')))

        self.text.on_pressed = lambda: evts.post(evts.EVT_PIBOOTH_CAPTURE)
        self.left_arrow.on_pressed = lambda: evts.post(evts.EVT_PIBOOTH_CAPTURE)
        self.image.on_pressed = lambda: evts.post(evts.EVT_PIBOOTH_PRINT)
        self.text_print.on_pressed = lambda: evts.post(evts.EVT_PIBOOTH_PRINT)
        self.right_arrow.on_pressed = lambda: evts.post(evts.EVT_PIBOOTH_PRINT)

    def resize(self, size):
        # Previous picture
        self.image.set_rect(0, 0, self.rect.width // 2, self.rect.height)

        # Take picture text
        text_border = 20
        self.text.set_text(get_translated_text('print'))  # In case of text has changed
        if self.arrow_location == self.ARROW_HIDDEN:
            self.text.set_align(pictures.ALIGN_CENTER)
            self.text.set_rect(self.rect.width // 2 + text_border, text_border,
                               self.rect.width // 2 - 2 * text_border,
                               self.rect.height - 2 * text_border)
        elif self.arrow_location == self.ARROW_BOTTOM:
            self.text.set_align(pictures.ALIGN_BOTTOM_CENTER)
            self.text.set_rect(self.rect.width // 2 + text_border, text_border,
                               self.rect.width // 2 - 2 * text_border,
                               self.rect.height * 0.6 - text_border)
        elif self.arrow_location == self.ARROW_TOUCH:
            self.text.set_align(pictures.ALIGN_BOTTOM_CENTER)
            self.text.set_rect(self.rect.width // 2 + text_border, text_border,
                               self.rect.width // 2 - 2 * text_border,
                               self.rect.height * 0.4 - text_border)
        else:
            self.text.set_align(pictures.ALIGN_TOP_CENTER)
            self.text.set_rect(self.rect.width // 2 + text_border, self.rect.height * 0.4,
                               self.rect.width // 2 - 2 * text_border,
                               self.rect.height * 0.6 - text_border)

        # Forget text
        self.text_print.set_text(get_translated_text('print_forget'))  # In case of text has changed
        rect = pygame.Rect(self.rect.centerx, 0, self.rect.width * 0.2, self.rect.height * 0.2)
        if self.arrow_location == self.ARROW_TOP:
            rect.top = self.rect.height * 0.12
        else:
            rect.bottom = self.rect.height - self.rect.height * 0.12
        self.text_print.set_rect(*rect)

        # Left arrow
        size = (self.rect.width * 0.1, self.rect.height * 0.1)
        if self.arrow_location == self.ARROW_TOP:
            y = self.rect.top + 10
        else:
            y = self.rect.bottom - size[1] - 10
        if self.arrow_location == self.ARROW_TOUCH:
            self.left_arrow.set_skin('touch.png')
            self.left_arrow.set_angle(60)
            self.left_arrow.set_flip(hflip=False)
        elif self.arrow_location in (self.ARROW_BOTTOM, self.ARROW_TOP):
            self.left_arrow.set_skin('arrow.png')
            self.left_arrow.set_angle(-60)
        if self.arrow_location != self.ARROW_HIDDEN:
            self.left_arrow.set_rect(self.rect.centerx, y, size[0], size[1])

        # Right arrow
        if self.arrow_location == self.ARROW_TOUCH:
            self.right_arrow.set_skin('touch_print.png')
            size = (self.rect.width * 0.15, self.rect.height * 0.15)
            x = self.rect.centerx + self.rect.width * 0.2
            y = self.rect.height // 2
        elif self.arrow_location in (self.ARROW_BOTTOM, self.ARROW_TOP):
            self.right_arrow.set_skin('arrow.png')
            size = (self.rect.width * 0.1, self.rect.height * 0.3)
            x = self.rect.centerx + self.rect.width // 4 - size[0] // 2
            if self.arrow_location == self.ARROW_TOP:
                y = self.rect.top + 10
            else:
                y = self.rect.bottom - size[1] - 10
        if self.arrow_location != self.ARROW_HIDDEN:
            self.right_arrow.set_rect(x, y, size[0], size[1])
