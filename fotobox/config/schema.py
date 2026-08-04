# -*- coding: utf-8 -*-
"""Typed configuration model and validation for the Fotobox app."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


class ConfigError(ValueError):
    """Raised when the configuration file is invalid, with a German message."""


@dataclass
class GeneralConfig:
    mock_hardware: bool = False
    session_timeout_seconds: int = 180
    log_level: str = "INFO"

    def validate(self) -> None:
        if self.session_timeout_seconds <= 0:
            raise ConfigError(
                "general.session_timeout_seconds muss größer als 0 sein.")


@dataclass
class GuiConfig:
    fullscreen: bool = True
    language: str = "de"
    idle_media_dir: str = "assets/idle"
    logo_path: str = "assets/logo.png"


@dataclass
class CameraConfig:
    backend: str = "gphoto2"
    model_hint: str = "Fujifilm X-T"
    capture_dir: str = "captures"
    live_preview: bool = True

    def validate(self) -> None:
        if self.backend not in ("gphoto2", "mock"):
            raise ConfigError(
                "camera.backend muss 'gphoto2' oder 'mock' sein, "
                "gefunden: '{}'.".format(self.backend))


@dataclass
class PrinterConfig:
    cups_printer_name: str = ""
    paper_size: str = "10x15"


@dataclass
class Package:
    id: str
    name: str
    price_cents: int
    currency: str = "EUR"
    copies: int = 1
    active: bool = True

    def validate(self) -> None:
        if not self.id:
            raise ConfigError("Ein Paket in 'packages' hat keine 'id'.")
        if self.price_cents <= 0:
            raise ConfigError(
                "Paket '{}': price_cents muss größer als 0 sein.".format(self.id))
        if self.copies <= 0:
            raise ConfigError(
                "Paket '{}': copies muss größer als 0 sein.".format(self.id))
        if not self.name:
            raise ConfigError("Paket '{}' hat keinen 'name'.".format(self.id))

    @property
    def price_display(self) -> str:
        return "{:.2f} {}".format(self.price_cents / 100, self.currency)


@dataclass
class SumUpConfig:
    sandbox: bool = False
    api_key: str = ""
    merchant_code: str = ""
    reader_id: str = ""
    checkout_reference_prefix: str = "FOTOBOX"
    poll_interval_seconds: int = 2
    poll_timeout_seconds: int = 90

    def validate(self, mock_hardware: bool) -> None:
        if mock_hardware:
            return
        missing = [
            field_name
            for field_name, value in (
                ("api_key", self.api_key),
                ("merchant_code", self.merchant_code),
                ("reader_id", self.reader_id),
            )
            if not value
        ]
        if missing:
            raise ConfigError(
                "SumUp-Konfiguration unvollständig, es fehlen: {}. "
                "Bitte im Admin-Bereich oder in config.yaml unter 'sumup' "
                "eintragen (Reader-Kopplung im Admin-Bereich möglich).".format(
                    ", ".join("sumup.{}".format(m) for m in missing)))
        if self.poll_interval_seconds <= 0 or self.poll_timeout_seconds <= 0:
            raise ConfigError(
                "sumup.poll_interval_seconds und poll_timeout_seconds "
                "müssen größer als 0 sein.")
        if self.poll_interval_seconds >= self.poll_timeout_seconds:
            raise ConfigError(
                "sumup.poll_interval_seconds muss kleiner als "
                "poll_timeout_seconds sein.")


@dataclass
class AdminConfig:
    pin_hash: str = ""


@dataclass
class Config:
    general: GeneralConfig = field(default_factory=GeneralConfig)
    gui: GuiConfig = field(default_factory=GuiConfig)
    camera: CameraConfig = field(default_factory=CameraConfig)
    printer: PrinterConfig = field(default_factory=PrinterConfig)
    packages: List[Package] = field(default_factory=list)
    sumup: SumUpConfig = field(default_factory=SumUpConfig)
    admin: AdminConfig = field(default_factory=AdminConfig)

    def validate(self) -> None:
        self.general.validate()
        self.camera.validate()
        if not self.packages:
            raise ConfigError(
                "Es ist kein Paket in 'packages' konfiguriert. "
                "Mindestens ein Paket wird benötigt.")
        ids = set()
        for pkg in self.packages:
            pkg.validate()
            if pkg.id in ids:
                raise ConfigError(
                    "Paket-ID '{}' ist mehrfach vergeben, IDs müssen "
                    "eindeutig sein.".format(pkg.id))
            ids.add(pkg.id)
        if not self.active_packages():
            raise ConfigError(
                "Kein Paket ist aktiv (active: true). Mindestens ein "
                "aktives Paket wird benötigt.")
        self.sumup.validate(self.general.mock_hardware)

    def active_packages(self) -> List[Package]:
        return [p for p in self.packages if p.active]
