# -*- coding: utf-8 -*-

from pibooth.utils import PollingTimer
from pibooth.view.pygame.sprites import BasePygameScene


class CaptureScene(BasePygameScene):

    def __init__(self):
        super().__init__()
        self.count_flash = 0
        self.is_flash_on = False
        self.saved_skin = None

        # Seconds between each flash
        self.flash_timer = PollingTimer(0.3)

    def resize(self, size):
        # Hide status bar
        self.status_bar.hide()

        # Capture
        self.image.set_rect(self.rect.width // 6, 10,
                            self.rect.width * 2 // 3, self.rect.height * 7 // 8)

    def update(self, events):
        if self.flash_timer.is_started() and self.flash_timer.is_timeout():
            self.trigger_flash()
        super().update(events)

    def set_capture_number(self, current, total):
        self.count_flash = 0

    def trigger_flash(self):
        self.flash_timer.start()
        self.is_flash_on = not self.is_flash_on
        if self.is_flash_on:
            self.count_flash += 1
            self.saved_skin = self.background.get_skin()
            self.background.set_skin((255, 255, 255))
        else:
            self.background.set_skin(self.saved_skin)
