# -*- coding: utf-8 -*-
"""Runtime session/application context shared between all states and the UI."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import List, Optional

from fotobox.config.schema import Config, Package


@dataclass
class SessionData:
    """Per-customer-session data, reset whenever we go back to idle."""

    selected_package: Optional[Package] = None
    captured_photos: List[str] = field(default_factory=list)
    chosen_photo: Optional[str] = None
    checkout_id: Optional[str] = None
    error_message: Optional[str] = None
    last_activity_ts: float = field(default_factory=time.monotonic)

    def touch(self) -> None:
        self.last_activity_ts = time.monotonic()

    def seconds_since_activity(self) -> float:
        return time.monotonic() - self.last_activity_ts

    def reset(self) -> None:
        self.selected_package = None
        self.captured_photos = []
        self.chosen_photo = None
        self.checkout_id = None
        self.error_message = None
        self.touch()


class AppContext:
    """Bundles config and hardware/service clients for use by states and UI.

    UI screens communicate with the active state through a single-slot
    "mailbox" (:meth:`set_ui_action` / :meth:`consume_ui_action`) instead of
    calling into the state machine directly, keeping the state machine as
    the single place that decides transitions.
    """

    def __init__(self, config: Config, camera, printer, payment_client, config_path: str):
        self.config = config
        self.camera = camera
        self.printer = printer
        self.payment_client = payment_client
        self.config_path = config_path
        self.session = SessionData()
        self._ui_action: Optional[str] = None

    def set_ui_action(self, action: str) -> None:
        self._ui_action = action

    def consume_ui_action(self) -> Optional[str]:
        action, self._ui_action = self._ui_action, None
        if action is not None:
            self.session.touch()
        return action
