# -*- coding: utf-8 -*-
"""Paketauswahl: Liste der aktiven Pakete aus der Konfiguration."""

from __future__ import annotations

from functools import partial

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

from .base import BoothScreen, big_button


class PackageScreen(BoothScreen):

    def on_pre_enter(self, *args) -> None:
        self.clear_widgets()
        layout = BoxLayout(orientation="vertical", padding=40, spacing=20)
        layout.add_widget(Label(text="Paket wählen", font_size="40sp",
                                 size_hint=(1, 0.2)))

        if self.app_ctx.session.error_message:
            layout.add_widget(Label(text=self.app_ctx.session.error_message,
                                     font_size="22sp", color=(1, 0.4, 0.4, 1),
                                     size_hint=(1, 0.15)))

        packages_row = BoxLayout(orientation="horizontal", spacing=20)
        for package in self.app_ctx.config.active_packages():
            label = "{}\n{}".format(package.name, package.price_display)
            btn = big_button(label)
            btn.bind(on_release=partial(self._select, package.id))
            packages_row.add_widget(btn)
        layout.add_widget(packages_row)
        self.add_widget(layout)

    def _select(self, package_id: str, *_args) -> None:
        self.app_ctx.set_ui_action("select_package:{}".format(package_id))
