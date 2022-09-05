# -*- coding: utf-8 -*-

from pibooth.view.base import BaseWindow
from pibooth.view.pygame.scenes.base import BasePygameScene, LeftArrowSprite, RightArrowSprite


class WaitScene(BasePygameScene):

    def __init__(self, name):
        super(WaitScene, self).__init__(name)
        self.left_arrow = LeftArrowSprite()
        self.add_sprite(self.left_arrow)
        self.right_arrow = RightArrowSprite()
        self.add_sprite(self.right_arrow)

    def _compute_position_and_size(self, events):
        # Previous picture
        self.image.set_rect(self.rect.centerx, 0, self.rect.width//2, self.rect.height)
        self.image.render()

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
            self.left_arrow.set_rect(x, y, size[0], size[1])
            self.left_arrow.render()

        # Right arrow
        size = (self.rect.width * 0.1, self.rect.height * 0.1)
        x = self.rect.centerx - size[0]
        if self.arrow_location == BaseWindow.ARROW_TOP:
            y = self.rect.top + 10
        else:
            y = self.rect.bottom - size[1] - 10
        if self.arrow_location == BaseWindow.ARROW_TOUCH:
            self.right_arrow.set_skin('touch_print.png')
        elif self.arrow_location in [BaseWindow.ARROW_BOTTOM, BaseWindow.ARROW_TOP]:
            self.right_arrow.set_skin('arrow.png')
            self.right_arrow.set_angle(-60)
        if self.arrow_location != BaseWindow.ARROW_HIDDEN:
            self.right_arrow.set_rect(x, y, size[0], size[1])
            self.right_arrow.render()

    def update_print_action(self, enabled=True):
        if enabled and self.right_arrow.location != BaseWindow.ARROW_HIDDEN:
            self.right_arrow.show()
        else:
            self.right_arrow.hide()
