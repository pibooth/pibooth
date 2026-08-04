# -*- coding: utf-8 -*-
"""Bezahl-Bildschirm: Aufforderung, die Karte an den SumUp Solo zu halten."""

from __future__ import annotations

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

from .base import BoothScreen


class PaymentScreen(BoothScreen):

    def on_pre_enter(self, *args) -> None:
        self.clear_widgets()
        package = self.app_ctx.session.selected_package
        layout = BoxLayout(orientation="vertical", padding=40, spacing=20)
        layout.add_widget(Label(text="Bitte Karte an das Kartenlesegerät halten",
                                 font_size="34sp"))
        if package is not None:
            layout.add_widget(Label(
                text="{} – {}".format(package.name, package.price_display),
                font_size="26sp"))
        layout.add_widget(Label(text="Zahlung wird verarbeitet ...", font_size="22sp"))
        self.add_widget(layout)
