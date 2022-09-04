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
        self.image.set_rect(self.background.rect.centerx, 0,
                            self.background.rect.width//2, self.background.rect.height)
        self.image.render()

        if self.left_arrow.location == BaseWindow.ARROW_BOTTOM:
            self.left_arrow.set_rect(0, 0, 50, 100)
            self.right_arrow.set_rect(200, 0, 50, 100)
        elif self.left_arrow.location == BaseWindow.ARROW_TOP:
            self.left_arrow.set_rect(0, 0, 50, 100)
            self.right_arrow.set_rect(200, 0, 50, 100)

        self.left_arrow.render()
        self.right_arrow.render()

    def update_print_action(self, enabled=True):
        if enabled and self.right_arrow.location != BaseWindow.ARROW_HIDDEN:
            self.right_arrow.show()
        else:
            self.right_arrow.hide()
