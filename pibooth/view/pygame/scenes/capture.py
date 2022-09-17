# -*- coding: utf-8 -*-

from pibooth.view.pygame.scenes.base import BasePygameScene


class CaptureScene(BasePygameScene):

    def __init__(self, name):
        super(CaptureScene, self).__init__(name)
        self.is_flash_on = False
        self.saved_skin = None

    def set_capture_number(self, current, total):
        pass

    def toggle_flash(self):
        self.is_flash_on = not self.is_flash_on
        if self.is_flash_on:
            self.saved_skin = self.background.get_skin()
            self.background.set_skin((255, 255, 255))
        else:
            self.background.set_skin(self.saved_skin)
