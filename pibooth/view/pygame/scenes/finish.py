# -*- coding: utf-8 -*-

from pibooth.language import get_translated_text
from pibooth.view.pygame.sprites import BasePygameScene, ImageSprite, TextSprite


class FinishScene(BasePygameScene):

    def __init__(self, name):
        super(FinishScene, self).__init__(name)
        self.left_image = self.add_sprite(ImageSprite('finish_left.png'))
        self.right_image = self.add_sprite(ImageSprite('finish_right.png'))
        self.text = self.add_sprite(TextSprite(get_translated_text('finished')))

    def resize(self, size):
        # Text
        self.text.set_text(get_translated_text('finished'))  # In case of text has changed
        self.text.set_rect(*self.rect.inflate(-self.rect.width // 2, -self.rect.height//2))

        # Final picture
        self.image.set_rect(*self.rect.inflate(-100, 0))

    def set_image(self, image):
        super(FinishScene, self).set_image(image)

        if not image:
            self.text.show()

            padding = self.rect.width // 4
            # Left image
            size = (padding - 20, self.rect.height * 0.3)
            self.left_image.set_rect(10, self.rect.centery - size[1], size[0], size[1])

            # Right image
            size = (padding - 20, self.rect.height * 0.3)
            self.right_image.set_rect(self.rect.right - size[0] - 10,
                                      self.rect.centery + size[1] // 2, size[0], size[1])
        else:
            self.text.hide()

            # Left image
            self.left_image.set_rect(0, 0, 100, 100)

            # Right image
            self.right_image.set_rect(self.rect.right - 100, self.rect.bottom - 100, 100, 100)
