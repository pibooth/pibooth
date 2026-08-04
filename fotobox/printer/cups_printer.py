# -*- coding: utf-8 -*-
"""Photo printing via CUPS (pycups)."""

from __future__ import annotations

import logging

LOGGER = logging.getLogger("fotobox.printer.cups")


class PrinterError(RuntimeError):
    """Raised when a printer is unreachable or a print job fails."""


class CupsPrinter:

    def __init__(self, printer_name: str, paper_size: str = "10x15"):
        try:
            import cups
        except ImportError as exc:
            raise PrinterError(
                "Das Python-Paket 'pycups' ist nicht installiert. "
                "Bitte 'pip install pycups' auf dem Raspberry Pi ausführen "
                "(benötigt libcups2-dev)."
            ) from exc
        if not printer_name:
            raise PrinterError(
                "printer.cups_printer_name ist nicht gesetzt. Bitte im "
                "Admin-Bereich oder in config.yaml eintragen (Name per "
                "'lpstat -p' ermittelbar).")
        self._cups = cups
        self._printer_name = printer_name
        self._paper_size = paper_size

    def is_available(self) -> bool:
        conn = self._cups.Connection()
        printers = conn.getPrinters()
        if self._printer_name not in printers:
            return False
        state = printers[self._printer_name].get("printer-state")
        # 3 = idle, 4 = processing, 5 = stopped (see CUPS IPP printer-state)
        return state in (3, 4)

    def print_photo(self, file_path: str, copies: int = 1) -> int:
        """Submit a print job. Returns the CUPS job id."""
        if not self.is_available():
            raise PrinterError(
                "Drucker '{}' ist nicht erreichbar oder gestoppt. "
                "Bitte Drucker prüfen ('lpstat -p').".format(self._printer_name))
        conn = self._cups.Connection()
        options = {
            "copies": str(max(1, copies)),
            "media": self._paper_size,
            "fit-to-page": "True",
        }
        try:
            job_id = conn.printFile(self._printer_name, file_path, "Fotobox", options)
        except self._cups.IPPError as exc:
            raise PrinterError("Druckauftrag fehlgeschlagen: {}".format(exc)) from exc
        LOGGER.info("Druckauftrag %s gestartet (%s Kopien) auf %s",
                    job_id, copies, self._printer_name)
        return job_id
