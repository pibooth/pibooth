# -*- coding: utf-8 -*-

from pibooth.language import get_translated_text
from pibooth.view.pygame.scenes.base import BasePygameScene, TextSprite


class ProcessingScene(BasePygameScene):

    def __init__(self, name):
        super(ProcessingScene, self).__init__(name)
        self.set_image('processing.png')
        self.text = self.add_sprite(TextSprite(get_translated_text('processing')))

    def resize(self, size):
        # Preview picture
        self.image.set_rect(*self.rect)

        # Text
        self.text.set_text(get_translated_text('processing'))  # In case of text has changed
        self.text.set_rect(10, self.rect.height * 3 // 4, self.rect.width - 20, self.rect.height // 4)
