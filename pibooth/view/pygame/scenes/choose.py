# -*- coding: utf-8 -*-

from pibooth.view.pygame.scenes.base import BasePygameScene


class ChooseScene(BasePygameScene):

    def __init__(self, name):
        super(ChooseScene, self).__init__(name)

    def _compute_position_and_size(self, events):
        print(events)

    def set_choices(self, choices):
        print(choices)
        for s in self.sprites.sprites():
            print(s, s.visible)
