# -*- coding: utf-8 -*-

import numpy
import pygame
try:
    import picamera2
    from picamera2 import Picamera2
    from libcamera import Transform
except ImportError:
    picamera2 = None  # picamera2 is optional
from PIL import ImageFilter
from pibooth.pictures import sizing
from pibooth.utils import LOGGER
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

    def __init__(self, libcamera_camera_proxy):
        super().__init__(libcamera_camera_proxy)
        self._preview_config = self._cam.create_preview_configuration()
        self._capture_config = self._cam.create_still_configuration()

    def _specific_initialization(self):
        """Camera initialization.
        """
        self._cam.stop()
        self._preview_config['format'] = 'BGR888'
        self._preview_config['transform'] = Transform(rotation=self.preview_rotation, hflip=self.preview_flip)
        self._cam.configure(self._preview_config)

        self._capture_config['size'] = self.resolution
        self._capture_config['transform'] = Transform(rotation=self.capture_rotation, hflip=self.capture_flip)
        self._cam.configure(self._preview_config)
        self._cam.start()

    def _show_overlay(self):
        """Add an image as an overlay.
        """
        self._overlay = self._build_overlay(self._rect.size, self._overlay_text, self._overlay_alpha)
        self._cam.set_overlay(numpy.array(self._overlay))

    def _hide_overlay(self):
        """Remove any existing overlay.
        """
        if self._overlay:
            self._cam.set_overlay(None)
            self._overlay = None
            self._overlay_text = None

    def _process_capture(self, capture_data):
        """Rework capture data.

        :param capture_data: couple (PIL Image, effect)
        :type capture_data: tuple
        """
        image, effect = capture_data
        if effect != 'none':
            image = image.filter(getattr(ImageFilter, effect.upper()))
        return image

    def get_preview_image(self):
        """Capture a new picture in a file.
        """
        return self._cam.capture_image('main')

    def preview(self, rect, flip=True):
        """Display a preview on the given Rect (flip if necessary).
        """
        # Define Rect() object for resizing preview captures to fit to the defined
        # preview rect keeping same aspect ratio than camera resolution.
        size = sizing.new_size_keep_aspect_ratio(self.resolution, (min(
            rect.width, self._cam.sensor_resolution[0]), min(rect.height, self._cam.sensor_resolution[1])))
        rect = pygame.Rect(rect.centerx - size[0] // 2, rect.centery - size[1] // 2,
                           size[0] - size[0] % 2, size[1] - size[1] % 2)

        self._preview_config['main']['size'] = rect.size
        self._preview_config['transform'] = Transform(rotation=self.preview_rotation, hflip=self.preview_flip)
        self._cam.switch_mode(self._preview_config)
        super().preview(rect, flip)

    def get_capture_image(self, effect=None):
        """Capture a new picture in a file.
        """
        self._cam.switch_mode(self._capture_config)
        image = self._cam.capture_image('main')
        self._captures.append((image, effect))
        return image

    def _specific_cleanup(self):
        """Close the camera driver, it's definitive.
        """
        self._cam.close()
