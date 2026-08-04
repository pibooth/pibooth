# -*- coding: utf-8 -*-
"""Fake SumUp client used when general.mock_hardware is true."""

from __future__ import annotations

import logging
import uuid

from .sumup_client import CheckoutResult, CheckoutStatus

LOGGER = logging.getLogger("fotobox.payment.mock")


class MockSumUpClient:

    def __init__(self, should_succeed: bool = True):
        self._should_succeed = should_succeed
        self.reader_id = "mock-reader"

    def pair_reader(self, pairing_code: str) -> str:
        LOGGER.info("[MOCK] Reader gekoppelt mit Code %s", pairing_code)
        return self.reader_id

    def create_checkout(self, amount_cents: int, currency: str, description: str,
                         reference_prefix: str = "FOTOBOX") -> CheckoutResult:
        checkout_id = "{}-{}".format(reference_prefix, uuid.uuid4().hex[:12])
        LOGGER.info("[MOCK] Checkout gestartet: %s (%s %s)",
                    checkout_id, amount_cents / 100, currency)
        return CheckoutResult(checkout_id=checkout_id, status=CheckoutStatus.PENDING)

    def get_checkout_status(self, checkout_id: str) -> CheckoutStatus:
        return CheckoutStatus.PAID if self._should_succeed else CheckoutStatus.FAILED

    def poll_until_complete(self, checkout_id: str, interval_seconds: int = 2,
                             timeout_seconds: int = 90) -> CheckoutStatus:
        return self.get_checkout_status(checkout_id)
