# -*- coding: utf-8 -*-
"""Startbildschirm: Werbeanimation/Logo, Tippen startet eine neue Sitzung."""

from __future__ import annotations

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

from .base import BoothScreen

ADMIN_TAP_COUNT = 5
ADMIN_TAP_WINDOW_SECONDS = 3.0


class IdleScreen(BoothScreen):

    def __init__(self, app_ctx, on_admin_requested=None, **kwargs):
        super().__init__(app_ctx, **kwargs)
        self._on_admin_requested = on_admin_requested
        self._admin_tap_times = []

        layout = BoxLayout(orientation="vertical", padding=40, spacing=20)
        layout.add_widget(Label(text="Fotobox", font_size="64sp"))
        layout.add_widget(Label(text="Zum Starten Bildschirm berühren",
                                 font_size="28sp"))
        self.add_widget(layout)
        layout.bind(on_touch_down=self._on_touch)

    def _on_touch(self, _widget, touch) -> bool:
        if not self.collide_point(*touch.pos):
            return False
        # A hidden corner-tap gesture (5 taps in the bottom-left corner
        # within 3s) opens the admin panel without a visible button.
        if touch.x < 120 and touch.y < 120:
            import time
            now = time.monotonic()
            self._admin_tap_times = [t for t in self._admin_tap_times
                                      if now - t < ADMIN_TAP_WINDOW_SECONDS]
            self._admin_tap_times.append(now)
            if len(self._admin_tap_times) >= ADMIN_TAP_COUNT:
                self._admin_tap_times = []
                if self._on_admin_requested:
                    self._on_admin_requested()
                return True
        self.app_ctx.set_ui_action("touch_start")
        return True
