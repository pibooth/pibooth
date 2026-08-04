# -*- coding: utf-8 -*-
from unittest.mock import patch

import pytest

from fotobox.admin import admin_panel
from fotobox.admin.admin_panel import AdminError
from fotobox.config.schema import (
    CameraConfig, Config, GeneralConfig, GuiConfig, Package, PrinterConfig,
    SumUpConfig,
)


def make_config():
    return Config(
        general=GeneralConfig(mock_hardware=True),
        gui=GuiConfig(),
        camera=CameraConfig(),
        printer=PrinterConfig(),
        packages=[Package(id="single", name="1 Foto", price_cents=500, copies=1)],
        sumup=SumUpConfig(),
    )


def test_verify_pin_allows_when_unset():
    config = make_config()
    assert admin_panel.verify_pin(config, "anything") is True


def test_set_pin_and_verify():
    config = make_config()
    admin_panel.set_pin(config, "1234")
    assert admin_panel.verify_pin(config, "1234") is True
    assert admin_panel.verify_pin(config, "0000") is False


def test_set_pin_rejects_short_pin():
    config = make_config()
    with pytest.raises(AdminError):
        admin_panel.set_pin(config, "12")


def test_upsert_package_updates_existing():
    config = make_config()
    admin_panel.upsert_package(config, "single", "1 Foto", price_cents=700, copies=2)
    pkg = next(p for p in config.packages if p.id == "single")
    assert pkg.price_cents == 700
    assert pkg.copies == 2


def test_upsert_package_adds_new():
    config = make_config()
    admin_panel.upsert_package(config, "double", "2 Fotos", price_cents=900, copies=2)
    assert any(p.id == "double" for p in config.packages)


def test_remove_last_package_rejected():
    config = make_config()
    with pytest.raises(AdminError):
        admin_panel.remove_package(config, "single")


@patch("fotobox.admin.admin_panel.SumUpClient")
def test_pair_reader_requires_credentials(client_cls):
    config = make_config()
    with pytest.raises(AdminError):
        admin_panel.pair_reader(config, "ABCD1234")
    client_cls.assert_not_called()


@patch("fotobox.admin.admin_panel.SumUpClient")
def test_pair_reader_stores_reader_id(client_cls):
    config = make_config()
    config.sumup.api_key = "key"
    config.sumup.merchant_code = "merchant"
    client_cls.return_value.pair_reader.return_value = "reader-42"

    reader_id = admin_panel.pair_reader(config, "ABCD1234")

    assert reader_id == "reader-42"
    assert config.sumup.reader_id == "reader-42"
