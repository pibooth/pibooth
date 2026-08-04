# -*- coding: utf-8 -*-
"""Danke-Bildschirm, kehrt nach kurzer Zeit automatisch zu idle zurück."""

from __future__ import annotations

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

from .base import BoothScreen


class ThankyouScreen(BoothScreen):

    def on_pre_enter(self, *args) -> None:
        self.clear_widgets()
        layout = BoxLayout(orientation="vertical", padding=40, spacing=20)
        layout.add_widget(Label(text="Danke und viel Spaß!", font_size="40sp"))
        self.add_widget(layout)
