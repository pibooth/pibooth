# -*- coding: utf-8 -*-

from pibooth.language import get_translated_text
from pibooth.view.pygame.scenes.base import BasePygameScene, TextSprite


class ProcessingScene(BasePygameScene):

    def __init__(self, name):
        super(ProcessingScene, self).__init__(name)
        self.image.set_skin('processing.png')
        self.image.show()
        self.text = TextSprite(get_translated_text('processing'))
        self.add_sprite(self.text)

    def resize(self, size):
        super(ProcessingScene, self).resize(size)

        # Preview picture
        self.image.set_rect(*self.rect)

        # Text
        self.text.set_text(get_translated_text('processing'))  # In case of text has changed
        self.text.set_rect(10, self.rect.height * 3 // 4, self.rect.width - 20, self.rect.height // 4)
