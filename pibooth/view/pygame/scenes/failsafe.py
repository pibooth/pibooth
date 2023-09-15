# -*- coding: utf-8 -*-

from pibooth.language import get_translated_text
from pibooth.view.pygame.window import PygameScene
from pibooth.view.pygame.sprites import TextSprite


class FailsafeScene(PygameScene):

    def __init__(self):
        super().__init__()
        self.text = TextSprite(self, get_translated_text('oops'))

    def resize(self, size):
        self.text.set_text(get_translated_text('oops'))  # In case of text has changed
        self.text.set_rect(*self.rect.inflate(-100, -100))
