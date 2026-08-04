# -*- coding: utf-8 -*-
"""gPhoto2-based tethering implementation for the Fujifilm X-T series.

Requires the ``gphoto2`` Python bindings (``pip install gphoto2``) and a
system installation of libgphoto2. The camera must be connected via USB and
set to "tethered shooting" / PC connection mode.
"""

from __future__ import annotations

import logging
import os
import time

from .base import BaseCamera, CameraError

LOGGER = logging.getLogger("fotobox.camera.gphoto2")


class FujifilmGphotoCamera(BaseCamera):

    def __init__(self):
        try:
            import gphoto2 as gp
        except ImportError as exc:
            raise CameraError(
                "Das Python-Paket 'gphoto2' ist nicht installiert. "
                "Bitte 'pip install gphoto2' auf dem Raspberry Pi ausführen."
            ) from exc
        self._gp = gp
        self._camera = None
        self._connect()

    def _connect(self) -> None:
        gp = self._gp
        try:
            camera = gp.Camera()
            camera.init()
        except gp.GPhoto2Error as exc:
            raise CameraError(
                "Kamera konnte nicht initialisiert werden. Ist die Fujifilm "
                "X-T per USB verbunden und im Tethering-Modus? ({})".format(exc)
            ) from exc
        self._camera = camera

    def is_connected(self) -> bool:
        if self._camera is None:
            return False
        try:
            self._camera.get_summary()
            return True
        except self._gp.GPhoto2Error:
            return False

    def _ensure_connected(self) -> None:
        if not self.is_connected():
            LOGGER.warning("Kamera nicht verbunden, versuche Neuverbindung ...")
            self._connect()

    def capture(self, dest_path: str) -> str:
        gp = self._gp
        self._ensure_connected()
        try:
            file_path = self._camera.capture(gp.GP_CAPTURE_IMAGE)
            camera_file = self._camera.file_get(
                file_path.folder, file_path.name, gp.GP_FILE_TYPE_NORMAL)
            os.makedirs(os.path.dirname(os.path.abspath(dest_path)), exist_ok=True)
            camera_file.save(dest_path)
        except gp.GPhoto2Error as exc:
            raise CameraError(
                "Aufnahme fehlgeschlagen: {}".format(exc)) from exc
        return dest_path

    def get_preview_frame(self):
        gp = self._gp
        if self._camera is None:
            return None
        try:
            camera_file = self._camera.capture_preview()
            return memoryview(camera_file.get_data_and_size()).tobytes()
        except gp.GPhoto2Error as exc:
            LOGGER.debug("Live-View-Frame nicht verfügbar: %s", exc)
            return None

    def close(self) -> None:
        if self._camera is not None:
            try:
                self._camera.exit()
            except self._gp.GPhoto2Error:
                pass
            self._camera = None
