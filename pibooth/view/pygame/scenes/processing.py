# -*- coding: utf-8 -*-

from pibooth.view.pygame.scenes.base import BasePygameScene


class ProcessingScene(BasePygameScene):

    def __init__(self, name):
        super(ProcessingScene, self).__init__(name)

    def _compute_position_and_size(self, events):
        print(events)
