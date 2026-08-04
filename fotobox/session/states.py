# -*- coding: utf-8 -*-
"""Concrete booth states: idle -> package_select -> payment_pending ->
capture -> review -> printing -> thankyou -> (back to idle), with a
failsafe state reachable from anywhere on error.
"""

from __future__ import annotations

import logging
import os
import threading
import time
from typing import Optional

from fotobox.camera.base import CameraError
from fotobox.payment.sumup_client import CheckoutStatus, PaymentError
from fotobox.printer.cups_printer import PrinterError

from .state_machine import State

LOGGER = logging.getLogger("fotobox.session.states")

THANKYOU_DISPLAY_SECONDS = 8
FAILSAFE_DISPLAY_SECONDS = 12


def _check_timeout(ctx) -> Optional[str]:
    """Shared inactivity check: reset to idle after general.session_timeout_seconds."""
    if ctx.session.seconds_since_activity() > ctx.config.general.session_timeout_seconds:
        LOGGER.info("Inaktivitäts-Timeout erreicht, Rückkehr zu idle.")
        return "idle"
    return None


class IdleState(State):
    name = "idle"

    def enter(self, ctx) -> None:
        ctx.session.reset()

    def validate(self, ctx) -> Optional[str]:
        action = ctx.consume_ui_action()
        if action == "touch_start":
            return "package_select"
        return None


class PackageSelectState(State):
    name = "package_select"

    def enter(self, ctx) -> None:
        ctx.session.touch()

    def validate(self, ctx) -> Optional[str]:
        action = ctx.consume_ui_action()
        if action and action.startswith("select_package:"):
            package_id = action.split(":", 1)[1]
            matches = [p for p in ctx.config.active_packages() if p.id == package_id]
            if not matches:
                LOGGER.warning("Unbekannte Paket-ID gewählt: %s", package_id)
                return None
            ctx.session.selected_package = matches[0]
            return "payment_pending"
        return _check_timeout(ctx)


class PaymentPendingState(State):
    name = "payment_pending"

    def __init__(self):
        self._thread: Optional[threading.Thread] = None
        self._status: Optional[CheckoutStatus] = None
        self._error: Optional[str] = None

    def enter(self, ctx) -> None:
        ctx.session.touch()
        ctx.session.error_message = None
        self._status = None
        self._error = None
        self._thread = threading.Thread(target=self._run_payment, args=(ctx,), daemon=True)
        self._thread.start()

    def _run_payment(self, ctx) -> None:
        package = ctx.session.selected_package
        try:
            result = ctx.payment_client.create_checkout(
                amount_cents=package.price_cents,
                currency=package.currency,
                description=package.name,
                reference_prefix=ctx.config.sumup.checkout_reference_prefix,
            )
            ctx.session.checkout_id = result.checkout_id
            self._status = ctx.payment_client.poll_until_complete(
                result.checkout_id,
                interval_seconds=ctx.config.sumup.poll_interval_seconds,
                timeout_seconds=ctx.config.sumup.poll_timeout_seconds,
            )
        except PaymentError as exc:
            self._error = str(exc)

    def validate(self, ctx) -> Optional[str]:
        if self._thread is not None and self._thread.is_alive():
            return None
        if self._error:
            ctx.session.error_message = self._error
            ctx.session.selected_package = None
            return "package_select"
        if self._status == CheckoutStatus.PAID:
            return "capture"
        if self._status in (CheckoutStatus.FAILED, None):
            ctx.session.error_message = "Zahlung wurde nicht abgeschlossen. Bitte erneut versuchen."
            ctx.session.selected_package = None
            return "package_select"
        return None

    def exit(self, ctx) -> None:
        self._thread = None


class CaptureState(State):
    name = "capture"

    def enter(self, ctx) -> None:
        ctx.session.touch()
        if not ctx.camera.is_connected():
            raise CameraError("Kamera ist nicht verbunden.")

    def validate(self, ctx) -> Optional[str]:
        action = ctx.consume_ui_action()
        if action == "trigger_capture":
            filename = "capture_{}.jpg".format(int(time.time() * 1000))
            dest = os.path.join(ctx.config.camera.capture_dir, filename)
            path = ctx.camera.capture(dest)
            ctx.session.captured_photos.append(path)
            ctx.session.chosen_photo = path
            return "review"
        return _check_timeout(ctx)


class ReviewState(State):
    name = "review"

    def enter(self, ctx) -> None:
        ctx.session.touch()

    def validate(self, ctx) -> Optional[str]:
        action = ctx.consume_ui_action()
        if action == "retake":
            return "capture"
        if action == "confirm_print":
            return "printing"
        return _check_timeout(ctx)


class PrintingState(State):
    name = "printing"

    def __init__(self):
        self._thread: Optional[threading.Thread] = None
        self._done = False
        self._error: Optional[str] = None

    def enter(self, ctx) -> None:
        ctx.session.touch()
        self._done = False
        self._error = None
        self._thread = threading.Thread(target=self._run_print, args=(ctx,), daemon=True)
        self._thread.start()

    def _run_print(self, ctx) -> None:
        try:
            copies = ctx.session.selected_package.copies
            ctx.printer.print_photo(ctx.session.chosen_photo, copies=copies)
            self._done = True
        except PrinterError as exc:
            self._error = str(exc)

    def validate(self, ctx) -> Optional[str]:
        if self._thread is not None and self._thread.is_alive():
            return None
        if self._error:
            ctx.session.error_message = self._error
            return "failsafe"
        if self._done:
            return "thankyou"
        return None

    def exit(self, ctx) -> None:
        self._thread = None


class ThankyouState(State):
    name = "thankyou"

    def enter(self, ctx) -> None:
        ctx.session.touch()

    def validate(self, ctx) -> Optional[str]:
        if ctx.session.seconds_since_activity() > THANKYOU_DISPLAY_SECONDS:
            return "idle"
        return None


class FailsafeState(State):
    name = "failsafe"

    def enter(self, ctx) -> None:
        LOGGER.error("Fehlerzustand: %s", ctx.session.error_message)
        ctx.session.touch()
        if ctx.camera is not None:
            try:
                ctx.camera.close()
            except Exception:
                LOGGER.exception("Fehler beim Schließen der Kamera im Fehlerzustand")

    def validate(self, ctx) -> Optional[str]:
        action = ctx.consume_ui_action()
        if action == "dismiss":
            return "idle"
        if ctx.session.seconds_since_activity() > FAILSAFE_DISPLAY_SECONDS:
            return "idle"
        return None


def build_state_machine(ctx):
    from .state_machine import StateMachine

    machine = StateMachine(ctx, failsafe_state_name="failsafe")
    for state in (
        IdleState(),
        PackageSelectState(),
        PaymentPendingState(),
        CaptureState(),
        ReviewState(),
        PrintingState(),
        ThankyouState(),
        FailsafeState(),
    ):
        machine.add_state(state)
    machine.start("idle")
    return machine
