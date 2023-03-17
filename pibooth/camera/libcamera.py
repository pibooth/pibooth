# -*- coding: utf-8 -*-

import time
import pygame
try:
    import picamera2
    from picamera2 import Picamera2, Preview
    from libcamera import Transform
except ImportError:
    picamera2 = None  # picamera2 is optional
from PIL import Image, ImageFilter
from pibooth.pictures import sizing
from pibooth.utils import PollingTimer, LOGGER
from pibooth.language import get_translated_text
from pibooth.camera.base import BaseCamera


def get_libcamera_camera_proxy(port=None):
    """Return camera proxy if a Raspberry Pi compatible camera is found
    else return None.

    :param port: look on given index number
    :type port: int
    """
    if not picamera2:
        return None  # picamera2 is not installed

    cameras = Picamera2.global_camera_info()
    if cameras:
        LOGGER.debug("Found libcamera cameras:")
        for index, info in enumerate(cameras):
            selected = ">" if index == port or (port is None and index == 0) else "*"
            LOGGER.debug("  %s %s : name-> %s | addr-> %s", selected, f"{index:02d}", info["Model"], info["Location"])

        if port is not None:
            return Picamera2(camera_num=port)
        return Picamera2()

    return None


class LibCamera(BaseCamera):

    """Libcamera camera management.
    """

    IMAGE_EFFECTS = [u'none',
                     u'blur',
                     u'contour',
                     u'detail',
                     u'edge_enhance',
                     u'edge_enhance_more',
                     u'emboss',
                     u'find_edges',
                     u'smooth',
                     u'smooth_more',
                     u'sharpen']

    def __init__(self, camera_proxy):
        super().__init__(camera_proxy)
        self._preview_config = self._cam.create_preview_configuration()
        self._capture_config = self._cam.create_still_configuration()

    def _specific_initialization(self):
        """Camera initialization.
        """
        self._preview_config.transform = Transform(hflip=self.preview_flip)
        self._cam.configure(self._preview_config)

        self._capture_config.size = self.resolution
        self._capture_config.transform = Transform(hflip=self.capture_flip)

    def _show_overlay(self):
        """Add an image as an overlay.
        """
        # Create an image padded to the required size (required by picamera)
        size = (((self._rect.width + 31) // 32) * 32, ((self._rect.height + 15) // 16) * 16)

        image = self.build_overlay(size, self._overlay_text, self._overlay_alpha)
        self._overlay = self._cam.add_overlay(image.tobytes(), image.size, layer=3,
                                              window=tuple(self._rect), fullscreen=False)

    def _hide_overlay(self):
        """Remove any existing overlay.
        """
        if self._overlay:
            self._cam.remove_overlay(self._overlay)
            self._overlay = None
            self._overlay_text = None

    def _process_capture(self, capture_data):
        """Rework capture data.

        :param capture_data: binary data as stream
        :type capture_data: :py:class:`io.BytesIO`
        """
        return capture_data

    def preview(self, rect, flip=True):
        """Display a preview on the given Rect (flip if necessary).
        """
        # Define Rect() object for resizing preview captures to fit to the defined
        # preview rect keeping same aspect ratio than camera resolution.
        size = sizing.new_size_keep_aspect_ratio(self.resolution, (rect.width, rect.height))
        self._rect = pygame.Rect(rect.centerx - size[0] // 2, rect.centery - size[1] // 2, size[0], size[1])
        self._cam.start_preview(Preview.DRM, x=self._rect.x, y=self._rect.y,
                                width=self._rect.width, height=self._rect.height)

        self.preview_flip = flip
        self._preview_config.transform = Transform(hflip=self.preview_flip)
        self._cam.configure(self._preview_config)
        self._cam.start()

    def stop_preview(self):
        """Stop the preview.
        """
        self._rect = None
        self._cam.stop_preview()
        self._hide_overlay()

    def get_capture_image(self, effect=None):
        """Capture a new picture in a file.
        """
        image = self._cam.switch_mode_and_capture_image(self._capture_config, "main")
        self._captures.append(image)
        return image

    def _specific_cleanup(self):
        """Close the camera driver, it's definitive.
        """
        self._cam.close()
