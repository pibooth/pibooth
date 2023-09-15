# -*- coding: utf-8 -*-

from pibooth.language import get_translated_text
from pibooth.view.pygame.window import PygameScene
from pibooth.view.pygame.sprites import TextSprite


class ChosenScene(PygameScene):

    def __init__(self):
        super().__init__()
        self.choice = 0
        self.text = TextSprite(self, get_translated_text('chosen'))

    def get_text(self):
        texts = []
        if get_translated_text('chosen'):
            texts.append(get_translated_text('chosen'))
        if get_translated_text(str(self.choice)):
            texts.append(get_translated_text(str(self.choice)))
        return "\n".join(texts)

    def resize(self, size):
        self.text.set_text(self.get_text())  # In case of text has changed
        self.text.set_rect(*self.rect.inflate(-100, -100))

    def set_selected_choice(self, choice):
        if self.choice != choice:
            self.choice = choice
            self.text.set_text(self.get_text())
