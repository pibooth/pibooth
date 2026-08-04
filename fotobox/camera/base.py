# -*- coding: utf-8 -*-
"""Camera interface used by the session state machine and UI."""

from __future__ import annotations

import abc
from typing import Optional


class CameraError(RuntimeError):
    """Raised when the camera is unreachable or a capture fails."""


class BaseCamera(abc.ABC):
    """Abstract camera used to take a photo for the current session."""

    @abc.abstractmethod
    def is_connected(self) -> bool:
        """Return True if the camera is reachable right now."""

    @abc.abstractmethod
    def capture(self, dest_path: str) -> str:
        """Trigger a capture and save the resulting JPEG to ``dest_path``.

        Returns the final file path actually written.
        """

    @abc.abstractmethod
    def get_preview_frame(self) -> Optional[bytes]:
        """Return the latest live-view JPEG frame bytes, or None if unavailable."""

    def close(self) -> None:
        """Release any camera resources. Optional to override."""
