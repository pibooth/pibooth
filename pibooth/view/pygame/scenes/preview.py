# -*- coding: utf-8 -*-

from pibooth.view.pygame.sprites import BasePygameScene, ImageSprite, DotsSprite


class PreviewScene(BasePygameScene):

    def __init__(self):
        super().__init__()
        self.left_image = self.add_sprite(ImageSprite('capture_left.png'))
        self.right_image = self.add_sprite(ImageSprite('capture_right.png'))
        self.dots = self.add_sprite(DotsSprite(4))

    def resize(self, size):
        # Preview capture
        self.image.set_rect(self.rect.width // 6, 10,
                            self.rect.width * 2 // 3, self.rect.height * 7 // 8)

        # Left image
        height = self.rect.height // 4
        size = (height, height)
        self.left_image.set_rect(10, self.rect.bottom - size[1], size[0] * 1.5, size[1])

        # Right image
        self.right_image.set_rect(self.rect.right - size[0] - 10, self.rect.bottom - size[1], size[0], size[1])

        # Dots
        self.dots.set_rect(self.rect.width // 6, self.rect.bottom - self.rect.height // 8 + 10,
                           self.rect.width * 2 // 3, self.rect.height // 8 - 10)

    def set_capture_number(self, current, total):
        self.dots.set_status(current, total)
