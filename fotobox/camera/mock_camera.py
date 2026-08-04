# -*- coding: utf-8 -*-
"""Fake camera used when general.mock_hardware is true (development/testing)."""

from __future__ import annotations

import base64
import os
import shutil

from .base import BaseCamera

_PLACEHOLDER_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")

# Minimal valid 1x1 pixel JPEG, used as a stand-in photo when no placeholder
# image is present under assets/mock_photo.jpg.
_TINY_JPEG_B64 = (
    "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAMCAgICAgMCAgIDAwMDBAYEBAQEBAgGBgUGCQgKCgkICQkKDA8MCgsOCwkJDRENDg8QEBEQCgwSExIQEw8QEBD/"
    "2wBDAQMDAwQDBAgEBAgQCwkLEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBD/"
    "wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAj/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/"
    "xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k="
)


class MockCamera(BaseCamera):

    def __init__(self):
        self._connected = True

    def is_connected(self) -> bool:
        return self._connected

    def capture(self, dest_path: str) -> str:
        os.makedirs(os.path.dirname(os.path.abspath(dest_path)), exist_ok=True)
        placeholder = os.path.join(_PLACEHOLDER_DIR, "mock_photo.jpg")
        if os.path.exists(placeholder):
            shutil.copyfile(placeholder, dest_path)
        else:
            with open(dest_path, "wb") as fh:
                fh.write(base64.b64decode(_TINY_JPEG_B64))
        return dest_path

    def get_preview_frame(self):
        return None

    def close(self) -> None:
        self._connected = False
