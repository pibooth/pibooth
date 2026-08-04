# -*- coding: utf-8 -*-
"""Druck-Bildschirm: Statusanzeige während des Druckvorgangs."""

from __future__ import annotations

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

from .base import BoothScreen


class PrintingScreen(BoothScreen):

    def on_pre_enter(self, *args) -> None:
        self.clear_widgets()
        layout = BoxLayout(orientation="vertical", padding=40, spacing=20)
        layout.add_widget(Label(text="Dein Foto wird gedruckt ...", font_size="34sp"))
        self.add_widget(layout)
