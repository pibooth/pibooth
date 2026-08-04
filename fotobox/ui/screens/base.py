# -*- coding: utf-8 -*-
"""Shared helpers for booth screens."""

from __future__ import annotations

from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen


class BoothScreen(Screen):
    """Base class for all booth screens: keeps a reference to the shared
    :class:`fotobox.session.session.AppContext` and exposes a hook that the
    app's Clock tick calls every frame so screens can refresh dynamic
    content (live preview, countdowns, ...).
    """

    def __init__(self, app_ctx, **kwargs):
        super().__init__(**kwargs)
        self.app_ctx = app_ctx

    def on_state_tick(self) -> None:
        """Called every frame while this screen is the active one."""


def big_button(text: str, **kwargs) -> Button:
    defaults = dict(font_size="32sp", size_hint=(1, 1))
    defaults.update(kwargs)
    return Button(text=text, **defaults)
