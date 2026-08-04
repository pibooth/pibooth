# -*- coding: utf-8 -*-
import time

import pytest

from fotobox.camera.mock_camera import MockCamera
from fotobox.config.schema import (
    CameraConfig, Config, GeneralConfig, GuiConfig, Package, PrinterConfig,
    SumUpConfig,
)
from fotobox.payment.mock_sumup import MockSumUpClient
from fotobox.printer.mock_printer import MockPrinter
from fotobox.session.session import AppContext
from fotobox.session.states import build_state_machine


def make_ctx(tmp_path, session_timeout_seconds=180, payment_succeeds=True):
    config = Config(
        general=GeneralConfig(mock_hardware=True,
                               session_timeout_seconds=session_timeout_seconds),
        gui=GuiConfig(),
        camera=CameraConfig(backend="mock", capture_dir=str(tmp_path)),
        printer=PrinterConfig(),
        packages=[Package(id="single", name="1 Foto", price_cents=500, copies=2)],
        sumup=SumUpConfig(),
    )
    ctx = AppContext(
        config=config,
        camera=MockCamera(),
        printer=MockPrinter(),
        payment_client=MockSumUpClient(should_succeed=payment_succeeds),
        config_path=str(tmp_path / "config.yaml"),
    )
    return ctx


def run_until(machine, ctx, predicate, max_steps=200):
    for _ in range(max_steps):
        if predicate():
            return True
        machine.process(0.05)
        time.sleep(0.01)
    return False


def test_happy_path_idle_to_thankyou(tmp_path):
    ctx = make_ctx(tmp_path)
    machine = build_state_machine(ctx)
    assert machine.active_state_name == "idle"

    ctx.set_ui_action("touch_start")
    machine.process(0.05)
    assert machine.active_state_name == "package_select"

    ctx.set_ui_action("select_package:single")
    machine.process(0.05)
    assert machine.active_state_name == "payment_pending"
    assert ctx.session.selected_package.id == "single"

    assert run_until(machine, ctx, lambda: machine.active_state_name == "capture")

    ctx.set_ui_action("trigger_capture")
    machine.process(0.05)
    assert machine.active_state_name == "review"
    assert ctx.session.chosen_photo is not None

    ctx.set_ui_action("confirm_print")
    machine.process(0.05)
    assert machine.active_state_name == "printing"

    assert run_until(machine, ctx, lambda: machine.active_state_name == "thankyou")


def test_retake_returns_to_capture(tmp_path):
    ctx = make_ctx(tmp_path)
    machine = build_state_machine(ctx)
    ctx.set_ui_action("touch_start")
    machine.process(0.05)
    ctx.set_ui_action("select_package:single")
    machine.process(0.05)
    assert run_until(machine, ctx, lambda: machine.active_state_name == "capture")

    ctx.set_ui_action("trigger_capture")
    machine.process(0.05)
    assert machine.active_state_name == "review"

    ctx.set_ui_action("retake")
    machine.process(0.05)
    assert machine.active_state_name == "capture"
    assert len(ctx.session.captured_photos) == 1  # not counted against package


def test_failed_payment_returns_to_package_select(tmp_path):
    ctx = make_ctx(tmp_path, payment_succeeds=False)
    machine = build_state_machine(ctx)
    ctx.set_ui_action("touch_start")
    machine.process(0.05)
    ctx.set_ui_action("select_package:single")
    machine.process(0.05)

    assert run_until(machine, ctx, lambda: machine.active_state_name == "package_select")
    assert ctx.session.error_message


def test_inactivity_timeout_resets_to_idle(tmp_path):
    ctx = make_ctx(tmp_path, session_timeout_seconds=0)
    machine = build_state_machine(ctx)
    ctx.set_ui_action("touch_start")
    machine.process(0.05)
    assert machine.active_state_name == "package_select"

    time.sleep(0.05)
    machine.process(0.05)
    assert machine.active_state_name == "idle"


def test_unknown_package_id_is_ignored(tmp_path):
    ctx = make_ctx(tmp_path)
    machine = build_state_machine(ctx)
    ctx.set_ui_action("touch_start")
    machine.process(0.05)

    ctx.set_ui_action("select_package:does-not-exist")
    machine.process(0.05)
    assert machine.active_state_name == "package_select"
    assert ctx.session.selected_package is None
