# -*- coding: utf-8 -*-
"""Vorschau-Bildschirm: Foto ansehen, wiederholen oder drucken."""

from __future__ import annotations

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image

from .base import BoothScreen, big_button


class ReviewScreen(BoothScreen):

    def on_pre_enter(self, *args) -> None:
        self.clear_widgets()
        layout = BoxLayout(orientation="vertical", padding=20, spacing=20)

        photo_path = self.app_ctx.session.chosen_photo
        if photo_path:
            layout.add_widget(Image(source=photo_path, size_hint=(1, 0.75)))

        buttons = BoxLayout(orientation="horizontal", size_hint=(1, 0.25), spacing=20)
        retake_btn = big_button("Nochmal")
        retake_btn.bind(on_release=lambda *_: self.app_ctx.set_ui_action("retake"))
        print_btn = big_button("Drucken")
        print_btn.bind(on_release=lambda *_: self.app_ctx.set_ui_action("confirm_print"))
        buttons.add_widget(retake_btn)
        buttons.add_widget(print_btn)
        layout.add_widget(buttons)

        self.add_widget(layout)
