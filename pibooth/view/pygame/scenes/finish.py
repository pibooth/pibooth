# -*- coding: utf-8 -*-

from pibooth.language import get_translated_text
from pibooth.view.pygame.window import PygameScene
from pibooth.view.pygame.sprites import ImageSprite, TextSprite


class FinishScene(PygameScene):

    def __init__(self):
        super().__init__()
        self.left_image = ImageSprite(self, 'finish_left.png')
        self.right_image = ImageSprite(self, 'finish_right.png')
        self.text = TextSprite(self, get_translated_text('finished'))

    def resize(self, size):
        # Show status bar
        self.status_bar.show()

        # Text
        self.text.set_text(get_translated_text('finished'))  # In case of text has changed
        self.text.set_rect(*self.rect.inflate(-self.rect.width // 2, -self.rect.height//2))

        # Final picture
        self.image.set_rect(*self.rect.inflate(-100, 0))

    def set_image(self, image, stream=False):
        super(FinishScene, self).set_image(image, stream)

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
