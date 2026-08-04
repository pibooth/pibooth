# -*- coding: utf-8 -*-
"""PIN-geschützter Admin-Bereich: Pakete, Drucker und SumUp-Zugangsdaten
direkt am Gerät bearbeiten, ohne die config.yaml manuell anzufassen.
"""

from __future__ import annotations

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput

from fotobox.admin import admin_panel
from fotobox.admin.admin_panel import AdminError

from .base import BoothScreen, big_button


class AdminScreen(BoothScreen):
    """Standalone Kivy screen for the admin panel.

    Not part of the booth state machine (it is entered via the hidden
    corner-tap gesture on the idle screen, see :class:`IdleScreen`), so it
    manages its own sub-navigation (PIN gate -> settings) internally.
    """

    def __init__(self, app_ctx, on_close=None, **kwargs):
        super().__init__(app_ctx, **kwargs)
        self._on_close = on_close
        self._pin_input = None
        self._status_label = None
        self._show_pin_gate()

    def on_pre_enter(self, *args) -> None:
        self._show_pin_gate()

    def _show_pin_gate(self) -> None:
        self.clear_widgets()
        layout = BoxLayout(orientation="vertical", padding=40, spacing=20)
        layout.add_widget(Label(text="Admin-Bereich – PIN eingeben", font_size="28sp"))
        self._pin_input = TextInput(
            password=True, multiline=False, input_filter="int",
            font_size="28sp", size_hint=(1, 0.2))
        layout.add_widget(self._pin_input)

        buttons = BoxLayout(size_hint=(1, 0.2), spacing=20)
        confirm_btn = big_button("Bestätigen")
        confirm_btn.bind(on_release=lambda *_: self._check_pin())
        cancel_btn = big_button("Abbrechen")
        cancel_btn.bind(on_release=lambda *_: self._close())
        buttons.add_widget(confirm_btn)
        buttons.add_widget(cancel_btn)
        layout.add_widget(buttons)
        self.add_widget(layout)

    def _check_pin(self) -> None:
        pin = self._pin_input.text
        if admin_panel.verify_pin(self.app_ctx.config, pin):
            self._show_settings()
        else:
            self._pin_input.text = ""
            self._pin_input.hint_text = "Falsche PIN, erneut versuchen"

    def _close(self) -> None:
        if self._on_close:
            self._on_close()

    def _show_settings(self) -> None:
        self.clear_widgets()
        root = BoxLayout(orientation="vertical", padding=20, spacing=10)
        root.add_widget(Label(text="Admin-Einstellungen", font_size="30sp",
                               size_hint=(1, 0.08)))

        scroll = ScrollView(size_hint=(1, 0.75))
        form = BoxLayout(orientation="vertical", spacing=15, size_hint_y=None,
                          padding=10)
        form.bind(minimum_height=form.setter("height"))

        cfg = self.app_ctx.config

        # Drucker
        form.add_widget(Label(text="Drucker (CUPS-Name)", size_hint_y=None, height=30))
        self._printer_input = TextInput(text=cfg.printer.cups_printer_name,
                                         multiline=False, size_hint_y=None, height=50)
        form.add_widget(self._printer_input)

        # SumUp
        form.add_widget(Label(text="SumUp API-Key", size_hint_y=None, height=30))
        self._api_key_input = TextInput(text=cfg.sumup.api_key, password=True,
                                         multiline=False, size_hint_y=None, height=50)
        form.add_widget(self._api_key_input)

        form.add_widget(Label(text="SumUp Merchant Code", size_hint_y=None, height=30))
        self._merchant_input = TextInput(text=cfg.sumup.merchant_code,
                                          multiline=False, size_hint_y=None, height=50)
        form.add_widget(self._merchant_input)

        form.add_widget(Label(
            text="Reader-ID: {}".format(cfg.sumup.reader_id or "(kein Reader gekoppelt)"),
            size_hint_y=None, height=30))
        form.add_widget(Label(text="Pairing-Code (am Kartenleser anzeigen lassen)",
                               size_hint_y=None, height=30))
        self._pairing_code_input = TextInput(multiline=False, size_hint_y=None, height=50)
        form.add_widget(self._pairing_code_input)
        pair_btn = big_button("Kartenleser koppeln", size_hint_y=None, height=60)
        pair_btn.bind(on_release=lambda *_: self._pair_reader())
        form.add_widget(pair_btn)

        # Pakete (nur Preis/Kopien des ersten aktiven Pakets als Kurz-Demo-Editor;
        # weitere Pakete werden weiterhin per config.yaml gepflegt)
        form.add_widget(Label(text="Pakete (Name / Preis in Cent / Kopien)",
                               size_hint_y=None, height=30))
        self._package_inputs = {}
        for package in cfg.packages:
            row = BoxLayout(size_hint_y=None, height=50, spacing=10)
            row.add_widget(Label(text=package.name, size_hint_x=0.4))
            price_input = TextInput(text=str(package.price_cents), multiline=False,
                                     input_filter="int", size_hint_x=0.3)
            copies_input = TextInput(text=str(package.copies), multiline=False,
                                      input_filter="int", size_hint_x=0.3)
            row.add_widget(price_input)
            row.add_widget(copies_input)
            form.add_widget(row)
            self._package_inputs[package.id] = (price_input, copies_input)

        scroll.add_widget(form)
        root.add_widget(scroll)

        self._status_label = Label(text="", size_hint=(1, 0.07), color=(1, 0.5, 0.5, 1))
        root.add_widget(self._status_label)

        buttons = BoxLayout(size_hint=(1, 0.1), spacing=20)
        save_btn = big_button("Speichern")
        save_btn.bind(on_release=lambda *_: self._save())
        close_btn = big_button("Schließen")
        close_btn.bind(on_release=lambda *_: self._close())
        buttons.add_widget(save_btn)
        buttons.add_widget(close_btn)
        root.add_widget(buttons)

        self.add_widget(root)

    def _pair_reader(self) -> None:
        cfg = self.app_ctx.config
        cfg.sumup.api_key = self._api_key_input.text
        cfg.sumup.merchant_code = self._merchant_input.text
        try:
            admin_panel.pair_reader(cfg, self._pairing_code_input.text)
            self._status_label.color = (0.5, 1, 0.5, 1)
            self._status_label.text = "Kartenleser erfolgreich gekoppelt."
        except AdminError as exc:
            self._status_label.color = (1, 0.5, 0.5, 1)
            self._status_label.text = str(exc)

    def _save(self) -> None:
        cfg = self.app_ctx.config
        try:
            admin_panel.update_printer(cfg, self._printer_input.text)
            admin_panel.update_sumup_credentials(
                cfg, api_key=self._api_key_input.text,
                merchant_code=self._merchant_input.text)
            for package in cfg.packages:
                price_input, copies_input = self._package_inputs[package.id]
                admin_panel.upsert_package(
                    cfg, package.id, package.name,
                    price_cents=int(price_input.text or 0),
                    copies=int(copies_input.text or 1),
                    currency=package.currency, active=package.active)
            admin_panel.save(cfg, self.app_ctx.config_path)
            self._status_label.color = (0.5, 1, 0.5, 1)
            self._status_label.text = "Gespeichert."
        except (AdminError, ValueError) as exc:
            self._status_label.color = (1, 0.5, 0.5, 1)
            self._status_label.text = str(exc)
