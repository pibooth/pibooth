# -*- coding: utf-8 -*-

from pibooth.language import get_translated_text
from pibooth.view.pygame.scenes.base import BasePygameScene, TextSprite


class FailsafeScene(BasePygameScene):

    def __init__(self, name):
        super(FailsafeScene, self).__init__(name)
        self.text = TextSprite(get_translated_text('oops'))
        self.add_sprite(self.text)

    def resize(self, size):
        super(FailsafeScene, self).resize(size)
        self.text.set_text(get_translated_text('oops'))  # In case of text has changed
        self.text.set_rect(*self.rect.inflate(-100, -100))
