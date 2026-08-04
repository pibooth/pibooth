# -*- coding: utf-8 -*-
"""Aufnahme-Bildschirm: Live-View der Kamera und Auslöser."""

from __future__ import annotations

import io

from kivy.core.image import Image as CoreImage
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label

from .base import BoothScreen, big_button


class CaptureScreen(BoothScreen):

    def __init__(self, app_ctx, **kwargs):
        super().__init__(app_ctx, **kwargs)
        self._preview = Image(size_hint=(1, 0.8))

    def on_pre_enter(self, *args) -> None:
        self.clear_widgets()
        layout = BoxLayout(orientation="vertical", padding=20, spacing=20)
        layout.add_widget(self._preview)
        shoot_btn = big_button("Auslösen", size_hint=(1, 0.2))
        shoot_btn.bind(on_release=lambda *_: self.app_ctx.set_ui_action("trigger_capture"))
        layout.add_widget(shoot_btn)
        self.add_widget(layout)

    def on_state_tick(self) -> None:
        frame = self.app_ctx.camera.get_preview_frame() if self.app_ctx.camera else None
        if frame:
            try:
                core_img = CoreImage(io.BytesIO(frame), ext="jpg")
                self._preview.texture = core_img.texture
            except Exception:
                pass
