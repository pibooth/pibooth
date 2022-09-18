# -*- coding: utf-8 -*-

from pibooth.language import get_translated_text
from pibooth.view.pygame.scenes.base import BasePygameScene, TextSprite


class ChosenScene(BasePygameScene):

    def __init__(self, name):
        super(ChosenScene, self).__init__(name)
        self.choice = 0
        self.text = self.add_sprite(TextSprite(get_translated_text('chosen')))

    def get_text(self):
        texts = []
        if get_translated_text('chosen'):
            texts.append(get_translated_text('chosen'))
        if get_translated_text(str(self.choice)):
            texts.append(get_translated_text(str(self.choice)))
        return "\n".join(texts)

    def resize(self, size):
        super(ChosenScene, self).resize(size)
        self.text.set_text(self.get_text())  # In case of text has changed
        self.text.set_rect(*self.rect.inflate(-100, -100))

    def set_selected_choice(self, choice):
        if self.choice != choice:
            self.choice = choice
            self.text.set_text(self.get_text())
