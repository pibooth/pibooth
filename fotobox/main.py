# -*- coding: utf-8 -*-
"""Fotobox entry point.

Usage:
    python -m fotobox.main [--config /path/to/config.yaml]
"""

from __future__ import annotations

import argparse
import logging
import os
import sys

DEFAULT_CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".fotobox", "config.yaml")


def _build_hardware(config, config_error_exit=True):
    from fotobox.camera.base import CameraError
    from fotobox.payment.sumup_client import PaymentError
    from fotobox.printer.cups_printer import PrinterError

    if config.general.mock_hardware:
        from fotobox.camera.mock_camera import MockCamera
        from fotobox.payment.mock_sumup import MockSumUpClient
        from fotobox.printer.mock_printer import MockPrinter

        return MockCamera(), MockPrinter(), MockSumUpClient()

    from fotobox.camera.fujifilm_gphoto import FujifilmGphotoCamera
    from fotobox.payment.sumup_client import SumUpClient
    from fotobox.printer.cups_printer import CupsPrinter

    try:
        camera = FujifilmGphotoCamera()
        printer = CupsPrinter(config.printer.cups_printer_name, config.printer.paper_size)
        payment_client = SumUpClient(
            api_key=config.sumup.api_key,
            merchant_code=config.sumup.merchant_code,
            reader_id=config.sumup.reader_id,
            sandbox=config.sumup.sandbox,
        )
    except (CameraError, PrinterError, PaymentError) as exc:
        logging.getLogger("fotobox.main").error("Hardware-Initialisierung fehlgeschlagen: %s", exc)
        if config_error_exit:
            sys.exit(1)
        raise
    return camera, printer, payment_client


def main() -> None:
    parser = argparse.ArgumentParser(description="Fotobox mit SumUp-Bezahlung")
    parser.add_argument("--config", default=DEFAULT_CONFIG_PATH,
                         help="Pfad zur config.yaml (Standard: {})".format(DEFAULT_CONFIG_PATH))
    args = parser.parse_args()

    from fotobox.config.loader import load_config
    from fotobox.config.schema import ConfigError

    try:
        config = load_config(args.config)
    except ConfigError as exc:
        print("Konfigurationsfehler: {}".format(exc), file=sys.stderr)
        sys.exit(1)

    logging.basicConfig(
        level=getattr(logging, config.general.log_level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    os.makedirs(config.camera.capture_dir, exist_ok=True)

    camera, printer, payment_client = _build_hardware(config)

    from fotobox.session.session import AppContext
    from fotobox.ui.app import FotoboxApp

    ctx = AppContext(config, camera, printer, payment_client, args.config)
    FotoboxApp(ctx).run()


if __name__ == "__main__":
    main()
