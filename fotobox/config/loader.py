# -*- coding: utf-8 -*-
"""Load, validate and persist the Fotobox YAML configuration."""

from __future__ import annotations

import hashlib
import logging
import os
import shutil

import yaml

from .schema import (
    AdminConfig,
    CameraConfig,
    Config,
    ConfigError,
    GeneralConfig,
    GuiConfig,
    Package,
    PrinterConfig,
    SumUpConfig,
)

LOGGER = logging.getLogger("fotobox.config")

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CONFIG_PATH = os.path.join(_THIS_DIR, "default_config.yaml")


def hash_pin(pin: str) -> str:
    """Hash an admin PIN for storage (never store the PIN itself)."""
    return hashlib.sha256(pin.encode("utf-8")).hexdigest()


def _build_config(raw: dict) -> Config:
    try:
        general = GeneralConfig(**raw.get("general", {}))
        gui = GuiConfig(**raw.get("gui", {}))
        camera = CameraConfig(**raw.get("camera", {}))
        printer = PrinterConfig(**raw.get("printer", {}))
        packages = [Package(**p) for p in raw.get("packages", [])]
        sumup = SumUpConfig(**raw.get("sumup", {}))
        admin = AdminConfig(**raw.get("admin", {}))
    except TypeError as exc:
        raise ConfigError(
            "config.yaml enthält ein unbekanntes oder fehlendes Feld: {}".format(exc)
        ) from exc

    return Config(
        general=general,
        gui=gui,
        camera=camera,
        printer=printer,
        packages=packages,
        sumup=sumup,
        admin=admin,
    )


def load_config(path: str) -> Config:
    """Load and validate configuration from ``path``.

    If ``path`` does not exist yet, it is created from the default template.
    """
    if not os.path.exists(path):
        LOGGER.info("config.yaml nicht gefunden, erstelle Standard-Konfiguration unter %s", path)
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        shutil.copyfile(DEFAULT_CONFIG_PATH, path)

    with open(path, "r", encoding="utf-8") as fh:
        raw = yaml.safe_load(fh) or {}

    config = _build_config(raw)
    config.validate()
    return config


def _config_to_dict(config: Config) -> dict:
    return {
        "general": vars(config.general),
        "gui": vars(config.gui),
        "camera": vars(config.camera),
        "printer": vars(config.printer),
        "packages": [vars(p) for p in config.packages],
        "sumup": vars(config.sumup),
        "admin": vars(config.admin),
    }


def save_config(config: Config, path: str) -> None:
    """Validate and persist ``config`` back to ``path`` (used by the admin panel)."""
    config.validate()
    tmp_path = path + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as fh:
        yaml.safe_dump(_config_to_dict(config), fh, allow_unicode=True, sort_keys=False)
    os.replace(tmp_path, path)
    LOGGER.info("Konfiguration gespeichert: %s", path)
