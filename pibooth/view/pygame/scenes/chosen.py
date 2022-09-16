# -*- coding: utf-8 -*-

from pibooth.view.pygame.scenes.base import BasePygameScene


class ChosenScene(BasePygameScene):

    def __init__(self, name):
        super(ChosenScene, self).__init__(name)

    def set_selected_choice(self, choice):
        pass
