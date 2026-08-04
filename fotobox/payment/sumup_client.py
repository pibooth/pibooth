# -*- coding: utf-8 -*-
"""SumUp Cloud API client for triggering payments on a paired Solo reader.

Flow implemented (SumUp Cloud API, https://developer.sumup.com/terminal-payments/cloud-api):

1. One-time pairing: the Solo reader displays a pairing code, which is
   exchanged via the API for a ``reader_id``. The ``reader_id`` is then
   stored in the app configuration (``sumup.reader_id``) and reused for
   every future checkout - pairing does not need to be repeated per payment.
2. Per payment: a checkout is created against the paired reader with an
   amount/currency. SumUp processes the tap/insert/swipe on the physical
   device; the app polls the checkout status until it leaves the pending
   state (PAID / FAILED) or a timeout is reached.

IMPORTANT: the exact request/response field names below follow SumUp's
publicly documented Cloud API shape as of this writing, but SumUp's API
reference (developer.sumup.com/api) could not be fetched directly while
building this client (returned HTTP 403 to automated requests). Before
going live, verify the endpoint paths and payload fields against the
current SumUp API reference / OpenAPI spec (https://github.com/sumup/sumup-openapi)
using your own SumUp developer account, and adjust ``_BASE_URL`` and the
request bodies in this file if they differ.
"""

from __future__ import annotations

import logging
import time
import uuid
from dataclasses import dataclass
from enum import Enum
from typing import Optional

import requests

LOGGER = logging.getLogger("fotobox.payment.sumup")

_BASE_URL = "https://api.sumup.com"


class PaymentError(RuntimeError):
    """Raised for SumUp API/network errors or a declined/timed-out payment."""


class CheckoutStatus(Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    FAILED = "FAILED"


@dataclass
class CheckoutResult:
    checkout_id: str
    status: CheckoutStatus


class SumUpClient:

    def __init__(self, api_key: str, merchant_code: str, reader_id: str = "",
                 sandbox: bool = False, timeout_seconds: int = 15):
        if not api_key or not merchant_code:
            raise PaymentError(
                "sumup.api_key und sumup.merchant_code müssen gesetzt sein.")
        self._api_key = api_key
        self._merchant_code = merchant_code
        self._reader_id = reader_id
        self._sandbox = sandbox
        self._timeout = timeout_seconds
        self._session = requests.Session()
        self._session.headers.update({
            "Authorization": "Bearer {}".format(api_key),
            "Content-Type": "application/json",
        })

    @property
    def reader_id(self) -> str:
        return self._reader_id

    def _url(self, path: str) -> str:
        return "{}{}".format(_BASE_URL, path)

    def pair_reader(self, pairing_code: str) -> str:
        """Pair a Solo reader using the code shown on its screen.

        Stores and returns the resulting ``reader_id``. Call this once from
        the admin panel when a (new) reader needs to be linked; the id should
        then be saved to ``sumup.reader_id`` in the configuration.
        """
        resp = self._session.post(
            self._url("/v0.1/merchants/{}/readers".format(self._merchant_code)),
            json={"pairing_code": pairing_code},
            timeout=self._timeout,
        )
        if resp.status_code >= 400:
            raise PaymentError(
                "Reader-Kopplung fehlgeschlagen ({}): {}".format(
                    resp.status_code, resp.text))
        data = resp.json()
        reader_id = data.get("id") or data.get("reader_id")
        if not reader_id:
            raise PaymentError(
                "Unerwartete Antwort bei Reader-Kopplung, keine Reader-ID "
                "erhalten: {}".format(data))
        self._reader_id = reader_id
        LOGGER.info("Reader erfolgreich gekoppelt: %s", reader_id)
        return reader_id

    def create_checkout(self, amount_cents: int, currency: str, description: str,
                         reference_prefix: str = "FOTOBOX") -> CheckoutResult:
        """Start a card payment on the paired reader. Returns immediately with
        a checkout id in PENDING state; use :meth:`poll_until_complete` to
        wait for the customer to tap/insert their card.
        """
        if not self._reader_id:
            raise PaymentError(
                "Kein Kartenleser gekoppelt (sumup.reader_id fehlt). Bitte "
                "im Admin-Bereich einen Reader koppeln.")
        reference = "{}-{}".format(reference_prefix, uuid.uuid4().hex[:12])
        resp = self._session.post(
            self._url("/v0.1/merchants/{}/readers/{}/checkout".format(
                self._merchant_code, self._reader_id)),
            json={
                "total_amount": {
                    "value": amount_cents,
                    "currency": currency,
                    "minor_unit": 2,
                },
                "description": description,
                "checkout_reference": reference,
            },
            timeout=self._timeout,
        )
        if resp.status_code >= 400:
            raise PaymentError(
                "Zahlung konnte nicht gestartet werden ({}): {}".format(
                    resp.status_code, resp.text))
        data = resp.json()
        checkout_id = data.get("id") or data.get("checkout_reference") or reference
        LOGGER.info("Checkout gestartet: %s (%s %s)", checkout_id, amount_cents / 100, currency)
        return CheckoutResult(checkout_id=checkout_id, status=CheckoutStatus.PENDING)

    def get_checkout_status(self, checkout_id: str) -> CheckoutStatus:
        resp = self._session.get(
            self._url("/v0.1/merchants/{}/readers/{}/checkout".format(
                self._merchant_code, self._reader_id)),
            params={"id": checkout_id},
            timeout=self._timeout,
        )
        if resp.status_code >= 400:
            raise PaymentError(
                "Zahlungsstatus konnte nicht abgefragt werden ({}): {}".format(
                    resp.status_code, resp.text))
        data = resp.json()
        status = str(data.get("status", "PENDING")).upper()
        try:
            return CheckoutStatus(status)
        except ValueError:
            LOGGER.warning("Unbekannter SumUp-Status '%s', werte als PENDING", status)
            return CheckoutStatus.PENDING

    def poll_until_complete(self, checkout_id: str, interval_seconds: int = 2,
                             timeout_seconds: int = 90) -> CheckoutStatus:
        """Poll the checkout status until PAID/FAILED or timeout.

        Raises :class:`PaymentError` on timeout so the caller can show a
        cancel/retry screen instead of blocking forever if the customer
        walks away without tapping their card.
        """
        deadline = time.monotonic() + timeout_seconds
        while time.monotonic() < deadline:
            status = self.get_checkout_status(checkout_id)
            if status != CheckoutStatus.PENDING:
                return status
            time.sleep(interval_seconds)
        raise PaymentError(
            "Zeitüberschreitung beim Warten auf die Zahlung (Kunde hat "
            "vermutlich keine Karte aufgelegt).")
