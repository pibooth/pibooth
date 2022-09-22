# -*- coding: utf-8 -*-

from pibooth.language import get_translated_text
from pibooth.view.pygame.scenes.base import BasePygameScene, TextSprite


class FailsafeScene(BasePygameScene):

    def __init__(self, name):
        super(FailsafeScene, self).__init__(name)
        self.text = self.add_sprite(TextSprite(get_translated_text('oops')))

    def resize(self, size):
        self.text.set_text(get_translated_text('oops'))  # In case of text has changed
        self.text.set_rect(*self.rect.inflate(-100, -100))
