# -*- coding: utf-8 -*-

from pibooth.view.pygame.scenes.base import BasePygameScene


class PreviewScene(BasePygameScene):

    def __init__(self, name):
        super(PreviewScene, self).__init__(name)

    def resize(self, size):
        super(PreviewScene, self).resize(size)

        # Preview picture
        self.image.set_rect(self.rect.centerx - self.rect.width//4, 10,
                            self.rect.width//2, self.rect.height * 7 // 8)

    def set_capture_number(self, current, total):
        pass
