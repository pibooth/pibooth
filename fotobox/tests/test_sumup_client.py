# -*- coding: utf-8 -*-
from unittest.mock import MagicMock, patch

import pytest

from fotobox.payment.sumup_client import (
    CheckoutStatus, PaymentError, SumUpClient,
)


def make_response(status_code=200, json_data=None, text=""):
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = json_data or {}
    resp.text = text
    return resp


def test_missing_credentials_raises():
    with pytest.raises(PaymentError):
        SumUpClient(api_key="", merchant_code="")


@patch("fotobox.payment.sumup_client.requests.Session")
def test_pair_reader_stores_id(session_cls):
    session = session_cls.return_value
    session.post.return_value = make_response(json_data={"id": "reader-123"})

    client = SumUpClient(api_key="key", merchant_code="merchant")
    reader_id = client.pair_reader("ABCD1234")

    assert reader_id == "reader-123"
    assert client.reader_id == "reader-123"


@patch("fotobox.payment.sumup_client.requests.Session")
def test_pair_reader_raises_on_http_error(session_cls):
    session = session_cls.return_value
    session.post.return_value = make_response(status_code=400, text="bad pairing code")

    client = SumUpClient(api_key="key", merchant_code="merchant")
    with pytest.raises(PaymentError):
        client.pair_reader("WRONG")


@patch("fotobox.payment.sumup_client.requests.Session")
def test_create_checkout_requires_reader(session_cls):
    client = SumUpClient(api_key="key", merchant_code="merchant")
    with pytest.raises(PaymentError):
        client.create_checkout(500, "EUR", "1 Foto")


@patch("fotobox.payment.sumup_client.requests.Session")
def test_create_checkout_returns_pending(session_cls):
    session = session_cls.return_value
    session.post.return_value = make_response(json_data={"id": "checkout-1"})

    client = SumUpClient(api_key="key", merchant_code="merchant", reader_id="reader-1")
    result = client.create_checkout(500, "EUR", "1 Foto")

    assert result.checkout_id == "checkout-1"
    assert result.status == CheckoutStatus.PENDING


@patch("fotobox.payment.sumup_client.requests.Session")
def test_poll_until_complete_returns_paid(session_cls):
    session = session_cls.return_value
    session.get.return_value = make_response(json_data={"status": "PAID"})

    client = SumUpClient(api_key="key", merchant_code="merchant", reader_id="reader-1")
    status = client.poll_until_complete("checkout-1", interval_seconds=1, timeout_seconds=5)

    assert status == CheckoutStatus.PAID


@patch("fotobox.payment.sumup_client.requests.Session")
def test_poll_until_complete_times_out(session_cls):
    session = session_cls.return_value
    session.get.return_value = make_response(json_data={"status": "PENDING"})

    client = SumUpClient(api_key="key", merchant_code="merchant", reader_id="reader-1")
    with pytest.raises(PaymentError):
        client.poll_until_complete("checkout-1", interval_seconds=1, timeout_seconds=1)
