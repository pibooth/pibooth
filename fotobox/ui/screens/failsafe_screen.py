# -*- coding: utf-8 -*-
"""Fehler-Bildschirm: wird bei Hardware-/Netzwerkfehlern angezeigt."""

from __future__ import annotations

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

from .base import BoothScreen, big_button


class FailsafeScreen(BoothScreen):

    def on_pre_enter(self, *args) -> None:
        self.clear_widgets()
        layout = BoxLayout(orientation="vertical", padding=40, spacing=20)
        layout.add_widget(Label(text="Es ist ein Fehler aufgetreten", font_size="34sp"))
        message = self.app_ctx.session.error_message or "Unbekannter Fehler."
        layout.add_widget(Label(text=message, font_size="22sp"))
        dismiss_btn = big_button("OK", size_hint=(1, 0.3))
        dismiss_btn.bind(on_release=lambda *_: self.app_ctx.set_ui_action("dismiss"))
        layout.add_widget(dismiss_btn)
        self.add_widget(layout)
