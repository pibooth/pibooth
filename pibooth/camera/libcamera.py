# -*- coding: utf-8 -*-

import numpy
import pygame
try:
    import picamera2
    from picamera2 import Picamera2, Preview
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

    def __init__(self, libcamera_camera_proxy):
        super().__init__(libcamera_camera_proxy)
        self._preview_config = self._cam.create_preview_configuration()
        self._capture_config = self._cam.create_still_configuration()

    def _specific_initialization(self):
        """Camera initialization.
        """
        self._cam.stop()
        self._preview_config['transform'] = Transform(hflip=self.preview_flip)
        self._cam.configure(self._preview_config)

        self._capture_config['size'] = self.resolution
        self._capture_config['transform'] = Transform(hflip=self.capture_flip)
        self._cam.start()

    def _show_overlay(self):
        """Add an image as an overlay.
        """
        # Create an image padded to the required size (required by picamera)
        size = (((self._rect.width + 31) // 32) * 32, ((self._rect.height + 15) // 16) * 16)

        self._overlay = self.build_overlay(size, self._overlay_text, self._overlay_alpha)
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

    def preview(self, rect, flip=True):
        """Display a preview on the given Rect (flip if necessary).
        """
        if self._cam._preview is not None:
            # Already running
            return

        self.preview_flip = flip
        self._preview_config['transform'] = Transform(hflip=self.preview_flip)

        # Define Rect() object for resizing preview captures to fit to the defined
        # preview rect keeping same aspect ratio than camera resolution.
        size = sizing.new_size_keep_aspect_ratio(self.resolution, (rect.width, rect.height))
        self._rect = pygame.Rect(rect.centerx - size[0] // 2, rect.centery - size[1] // 2, size[0], size[1])

        self._cam.stop()
        self._cam.configure(self._preview_config)
        self._cam.start_preview(Preview.DRM, x=self._rect.x, y=self._rect.y,
                                width=self._rect.width, height=self._rect.height)
        self._cam.start()

    def stop_preview(self):
        """Stop the preview.
        """
        self._rect = None
        self._hide_overlay()
        if self._cam._preview is not None:
            self._cam.stop_preview()

    def get_capture_image(self, effect=None):
        """Capture a new picture in a file.
        """
        image = self._cam.switch_mode_and_capture_image(self._capture_config, "main")
        self._captures.append((image, effect))
        return image

    def _specific_cleanup(self):
        """Close the camera driver, it's definitive.
        """
        self._cam.close()
