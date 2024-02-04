# -*- coding: utf-8 -*-

import pygame
from pibooth.utils import PollingTimer
from pibooth import evts, fonts
from pibooth.language import get_translated_text
from pibooth.view.pygame.window import PygameScene
from pibooth.view.pygame.sprites import LeftArrowSprite, RightArrowSprite, ImageSprite, TextSprite


class WaitScene(PygameScene):

    def __init__(self):
        super().__init__()
        self.left_arrow = LeftArrowSprite(self)
        self.right_arrow = RightArrowSprite(self)
        self.text = TextSprite(self, get_translated_text('intro'))
        self.text_print = TextSprite(self, get_translated_text('intro_print'))
        self.image_check = ImageSprite(self, 'action_done.png')
        self.image_check.hide()

        self.printer_ongoing_timer = PollingTimer(1, False)

        self.text.on_pressed = lambda: evts.post(evts.EVT_PIBOOTH_CAPTURE)
        self.left_arrow.on_pressed = lambda: evts.post(evts.EVT_PIBOOTH_CAPTURE)
        self.image.on_pressed = self.on_print_event
        self.text_print.on_pressed = self.on_print_event
        self.right_arrow.on_pressed = self.on_print_event

    def on_print_event(self):
        self.image.hide()  # Do not show image after click, there is a timer before
        self.image_check.show()
        self.printer_ongoing_timer.start()
        evts.post(evts.EVT_PIBOOTH_PRINT)

    def resize(self, size):
        # Previous picture
        self.image.set_rect(self.rect.centerx, 0, self.rect.width // 2, self.rect.height)
        self.image_check.set_rect(*self.image.rect.inflate(-self.image.rect.width // 2,
                                                           -self.image.rect.width // 2))

        # Take picture text
        text_border = 20
        self.text.set_text(get_translated_text('intro'))  # In case of text has changed
        if self.arrow_location == self.ARROW_HIDDEN:
            self.text.set_align(fonts.ALIGN_CENTER)
            self.text.set_rect(text_border, text_border,
                               self.rect.width // 2 - 2 * text_border,
                               self.rect.height - 2 * text_border)
        elif self.arrow_location == self.ARROW_BOTTOM:
            self.text.set_align(fonts.ALIGN_BOTTOM_CENTER)
            self.text.set_rect(text_border, text_border,
                               self.rect.width // 2 - 2 * text_border,
                               self.rect.height * 0.6 - text_border)
        elif self.arrow_location == self.ARROW_TOUCH:
            self.text.set_align(fonts.ALIGN_BOTTOM_CENTER)
            self.text.set_rect(text_border, text_border,
                               self.rect.width // 2 - 2 * text_border,
                               self.rect.height * 0.4 - text_border)
        else:
            self.text.set_align(fonts.ALIGN_TOP_CENTER)
            self.text.set_rect(text_border, self.rect.height * 0.4,
                               self.rect.width // 2 - 2 * text_border,
                               self.rect.height * 0.6 - text_border)

        # Print text
        self.text_print.set_text(get_translated_text('intro_print'))  # In case of text has changed
        rect = pygame.Rect(self.rect.width * 0.3, 0, self.rect.width * 0.2, self.rect.height * 0.2)
        if self.arrow_location == self.ARROW_TOP:
            rect.top = self.rect.height * 0.11
        else:
            rect.bottom = self.rect.height - self.rect.height * 0.11
        self.text_print.set_rect(*rect)

        # Left arrow
        if self.arrow_location == self.ARROW_TOUCH:
            self.left_arrow.set_skin('touch_camera.png')
            size = (self.rect.width * 0.15, self.rect.height * 0.15)
            x = self.rect.width * 0.2
            y = self.rect.height // 2
        elif self.arrow_location in (self.ARROW_BOTTOM, self.ARROW_TOP):
            self.left_arrow.set_skin('arrow.png')
            size = (self.rect.width * 0.1, self.rect.height * 0.3)
            x = self.rect.left + self.rect.width // 4 - size[0] // 2
            if self.arrow_location == self.ARROW_TOP:
                y = self.rect.top + 10
            else:
                y = self.rect.bottom - size[1] - 10
        if self.arrow_location != self.ARROW_HIDDEN:
            self.left_arrow.set_rect(x, y, size[0], size[1])

        # Right arrow
        size = (self.rect.width * 0.1, self.rect.height * 0.1)
        x = self.rect.centerx - size[0]
        if self.arrow_location == self.ARROW_TOP:
            y = self.rect.top + 10
        else:
            y = self.rect.bottom - size[1] - 10
        if self.arrow_location == self.ARROW_TOUCH:
            self.right_arrow.set_skin('touch_print.png')
            self.right_arrow.set_flip(hflip=False)
        elif self.arrow_location in (self.ARROW_BOTTOM, self.ARROW_TOP):
            self.right_arrow.set_skin('arrow.png')
            self.right_arrow.set_angle(-60)
        if self.arrow_location != self.ARROW_HIDDEN:
            self.right_arrow.set_rect(x, y, size[0], size[1])

    def update(self, events):

        if self.printer_ongoing_timer.is_started() and self.printer_ongoing_timer.is_timeout():
            self.image.show()
            self.image_check.hide()
            self.printer_ongoing_timer.reset()

        super().update(events)

    def update_print_action(self, enabled=True):
        if enabled:
            self.text_print.show()
            if self.arrow_location != self.ARROW_HIDDEN:
                self.right_arrow.show()
            self.image.on_pressed = self.on_print_event
        else:
            self.text_print.hide()
            if self.arrow_location != self.ARROW_HIDDEN:
                self.right_arrow.hide()
            self.image.on_pressed = None
