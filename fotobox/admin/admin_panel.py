# -*- coding: utf-8 -*-
"""PIN-protected administration operations: edit packages/prices, printer,
SumUp credentials, and pair a new card reader. Kept UI-independent so it can
be unit tested and reused by any screen implementation.
"""

from __future__ import annotations

from typing import Optional

from fotobox.config import loader
from fotobox.config.schema import Config, ConfigError, Package
from fotobox.payment.sumup_client import PaymentError, SumUpClient


class AdminError(RuntimeError):
    pass


def verify_pin(config: Config, pin: str) -> bool:
    if not config.admin.pin_hash:
        # No PIN set yet: first-time setup is allowed in without a PIN.
        return True
    return loader.hash_pin(pin) == config.admin.pin_hash


def set_pin(config: Config, new_pin: str) -> None:
    if not new_pin or len(new_pin) < 4:
        raise AdminError("Die PIN muss mindestens 4 Ziffern haben.")
    config.admin.pin_hash = loader.hash_pin(new_pin)


def upsert_package(config: Config, package_id: str, name: str, price_cents: int,
                    copies: int, currency: str = "EUR", active: bool = True) -> None:
    existing = next((p for p in config.packages if p.id == package_id), None)
    if existing is not None:
        existing.name = name
        existing.price_cents = price_cents
        existing.copies = copies
        existing.currency = currency
        existing.active = active
    else:
        config.packages.append(Package(
            id=package_id, name=name, price_cents=price_cents,
            copies=copies, currency=currency, active=active))
    try:
        config.validate()
    except ConfigError as exc:
        raise AdminError(str(exc)) from exc


def remove_package(config: Config, package_id: str) -> None:
    config.packages = [p for p in config.packages if p.id != package_id]
    try:
        config.validate()
    except ConfigError as exc:
        raise AdminError(str(exc)) from exc


def update_printer(config: Config, cups_printer_name: str, paper_size: Optional[str] = None) -> None:
    config.printer.cups_printer_name = cups_printer_name
    if paper_size:
        config.printer.paper_size = paper_size


def update_sumup_credentials(config: Config, api_key: Optional[str] = None,
                              merchant_code: Optional[str] = None) -> None:
    if api_key:
        config.sumup.api_key = api_key
    if merchant_code:
        config.sumup.merchant_code = merchant_code


def pair_reader(config: Config, pairing_code: str) -> str:
    """Pair a new SumUp Solo reader and store its reader_id in the config."""
    if not config.sumup.api_key or not config.sumup.merchant_code:
        raise AdminError(
            "API-Key und Merchant Code müssen zuerst gesetzt werden, bevor "
            "ein Kartenleser gekoppelt werden kann.")
    client = SumUpClient(
        api_key=config.sumup.api_key,
        merchant_code=config.sumup.merchant_code,
        sandbox=config.sumup.sandbox,
    )
    try:
        reader_id = client.pair_reader(pairing_code)
    except PaymentError as exc:
        raise AdminError(str(exc)) from exc
    config.sumup.reader_id = reader_id
    return reader_id


def save(config: Config, config_path: str) -> None:
    try:
        loader.save_config(config, config_path)
    except ConfigError as exc:
        raise AdminError(str(exc)) from exc
