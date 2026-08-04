# -*- coding: utf-8 -*-
"""Fake printer used when general.mock_hardware is true."""

from __future__ import annotations

import logging

LOGGER = logging.getLogger("fotobox.printer.mock")


class MockPrinter:

    def __init__(self):
        self._next_job_id = 1

    def is_available(self) -> bool:
        return True

    def print_photo(self, file_path: str, copies: int = 1) -> int:
        job_id = self._next_job_id
        self._next_job_id += 1
        LOGGER.info("[MOCK] Druckauftrag %s: %s (%s Kopien)", job_id, file_path, copies)
        return job_id
