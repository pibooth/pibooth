# -*- coding: utf-8 -*-
"""Kivy application: wires the state machine to a ScreenManager and drives
the enter/do/validate loop from Kivy's Clock.
"""

from __future__ import annotations

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.screenmanager import NoTransition, ScreenManager

from fotobox.session.states import build_state_machine

from .screens.admin_screen import AdminScreen
from .screens.capture_screen import CaptureScreen
from .screens.failsafe_screen import FailsafeScreen
from .screens.idle_screen import IdleScreen
from .screens.package_screen import PackageScreen
from .screens.payment_screen import PaymentScreen
from .screens.printing_screen import PrintingScreen
from .screens.review_screen import ReviewScreen
from .screens.thankyou_screen import ThankyouScreen

TICK_INTERVAL_SECONDS = 1.0 / 20.0
ADMIN_SCREEN_NAME = "admin"


class FotoboxApp(App):

    def __init__(self, app_ctx, **kwargs):
        super().__init__(**kwargs)
        self.app_ctx = app_ctx
        self.state_machine = build_state_machine(app_ctx)
        self.sm = None

    def build(self):
        Window.fullscreen = "auto" if self.app_ctx.config.gui.fullscreen else False

        self.sm = ScreenManager(transition=NoTransition())
        self.sm.add_widget(IdleScreen(self.app_ctx, name="idle",
                                       on_admin_requested=self._open_admin))
        self.sm.add_widget(PackageScreen(self.app_ctx, name="package_select"))
        self.sm.add_widget(PaymentScreen(self.app_ctx, name="payment_pending"))
        self.sm.add_widget(CaptureScreen(self.app_ctx, name="capture"))
        self.sm.add_widget(ReviewScreen(self.app_ctx, name="review"))
        self.sm.add_widget(PrintingScreen(self.app_ctx, name="printing"))
        self.sm.add_widget(ThankyouScreen(self.app_ctx, name="thankyou"))
        self.sm.add_widget(FailsafeScreen(self.app_ctx, name="failsafe"))
        self.sm.add_widget(AdminScreen(self.app_ctx, name=ADMIN_SCREEN_NAME,
                                        on_close=self._close_admin))

        self._pre_admin_state = None
        Clock.schedule_interval(self._tick, TICK_INTERVAL_SECONDS)
        return self.sm

    def _open_admin(self) -> None:
        self._pre_admin_state = self.state_machine.active_state_name
        self.sm.current = ADMIN_SCREEN_NAME

    def _close_admin(self) -> None:
        self.sm.current = self._pre_admin_state or "idle"

    def _tick(self, dt: float) -> None:
        if self.sm.current == ADMIN_SCREEN_NAME:
            return  # Admin panel manages its own navigation while open.

        self.state_machine.process(dt)
        active = self.state_machine.active_state_name
        if active and self.sm.current != active:
            self.sm.current = active

        screen = self.sm.get_screen(active) if active else None
        if screen is not None:
            screen.on_state_tick()
