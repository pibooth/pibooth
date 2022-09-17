# -*- coding: utf-8 -*-

from pibooth.view.pygame.scenes.base import BasePygameScene, ImageSprite


class PreviewScene(BasePygameScene):

    def __init__(self, name):
        super(PreviewScene, self).__init__(name)
        self.left_image = ImageSprite('capture_left.png')
        self.add_sprite(self.left_image)
        self.right_image = ImageSprite('capture_right.png')
        self.add_sprite(self.right_image)

    def resize(self, size):
        super(PreviewScene, self).resize(size)

        # Preview picture
        self.image.set_rect(self.rect.centerx - self.rect.width//4, 10,
                            self.rect.width//2, self.rect.height * 7 // 8)

        # Left image
        height = self.rect.height / 4
        size = (height, height)
        self.left_image.set_rect(10, self.rect.bottom - size[1], size[0] * 1.5, size[1])

        # Right image
        self.right_image.set_rect(self.rect.right - size[0] - 10, self.rect.bottom - size[1], size[0], size[1])

    def set_capture_number(self, current, total):
        pass
