# -*- coding: utf-8 -*-
import os

import pytest
import yaml

from fotobox.config.loader import load_config, save_config, hash_pin
from fotobox.config.schema import (
    CameraConfig, Config, ConfigError, GeneralConfig, GuiConfig, Package,
    PrinterConfig, SumUpConfig,
)


def test_load_config_creates_default_template_when_missing(tmp_path):
    """The default template ships without SumUp credentials, so validation
    fails on a truly fresh install - but the template must still be written
    to disk so the operator has something to fill in."""
    config_path = str(tmp_path / "config.yaml")
    assert not os.path.exists(config_path)

    with pytest.raises(ConfigError, match="SumUp"):
        load_config(config_path)

    assert os.path.exists(config_path)
    raw = yaml.safe_load(open(config_path, encoding="utf-8"))
    assert raw["general"]["session_timeout_seconds"] == 180
    assert len(raw["packages"]) == 3


def _valid_config():
    return Config(
        general=GeneralConfig(mock_hardware=True),
        gui=GuiConfig(),
        camera=CameraConfig(),
        printer=PrinterConfig(),
        packages=[Package(id="single", name="1 Foto", price_cents=500, copies=1)],
        sumup=SumUpConfig(),
    )


def test_load_config_rejects_empty_packages(tmp_path):
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        "general:\n  mock_hardware: true\npackages: []\n", encoding="utf-8")

    with pytest.raises(ConfigError):
        load_config(str(config_path))


def test_load_config_rejects_missing_sumup_credentials(tmp_path):
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        "general:\n  mock_hardware: false\n"
        "packages:\n"
        "  - id: single\n    name: '1 Foto'\n    price_cents: 500\n    copies: 1\n",
        encoding="utf-8")

    with pytest.raises(ConfigError, match="SumUp"):
        load_config(str(config_path))


def test_save_config_round_trip(tmp_path):
    config_path = str(tmp_path / "config.yaml")
    config = _valid_config()
    config.printer.cups_printer_name = "MyPrinter"
    config.admin.pin_hash = hash_pin("1234")

    save_config(config, config_path)
    reloaded = load_config(config_path)

    assert reloaded.printer.cups_printer_name == "MyPrinter"
    assert reloaded.admin.pin_hash == hash_pin("1234")


def test_save_config_rejects_invalid_state(tmp_path):
    config_path = str(tmp_path / "config.yaml")
    config = _valid_config()
    config.packages = []

    with pytest.raises(ConfigError):
        save_config(config, config_path)
