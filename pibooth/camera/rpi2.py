# -*- coding: utf-8 -*-

import time
import pygame
from io import BytesIO
try:
    import numpy as np
except ImportError:
    np = None
try:
    from picamera2 import Picamera2
except ImportError:
    Picamera2 = None
from PIL import Image, ImageFilter
from pibooth.pictures import sizing
from pibooth.utils import PoolingTimer, LOGGER
from pibooth.language import get_translated_text
from pibooth.camera.base import BaseCamera


def get_rpi2_camera_proxy(port=None):
    """Return camera proxy if a Raspberry Pi camera (libcamera/picamera2) is found
    else return None.

    :param port: optional camera index (currently unused, for API consistency)
    :type port: int
    """
    if Picamera2 is None or np is None:
        return None
    try:
        cam = Picamera2()
        cam.configure(cam.create_preview_configuration())
        cam.start()
        return cam
    except Exception as ex:
        LOGGER.debug("Picamera2 not available: %s", ex)
        return None


class Rpi2Camera(BaseCamera):

    """Camera management using picamera2 (libcamera).
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
        super(Rpi2Camera, self).__init__(camera_proxy)
        self._overlay_alpha = 255
        self._still_config = None
        self._preview_config = None

    def _specific_initialization(self):
        """Camera initialization.
        """
        self._cam.stop()
        self._preview_config = self._cam.create_preview_configuration(
            {"size": (min(1280, self.resolution[0]), min(720, self.resolution[1]))}
        )
        self._still_config = self._cam.create_still_configuration(
            {"size": self.resolution}
        )
        self._cam.configure(self._preview_config)
        self._cam.start()
        LOGGER.debug("Picamera2 configured: preview and still %s", self.resolution)

    def _show_overlay(self, text, alpha):
        """Add an image as an overlay (software overlay).
        """
        if self._window:
            rect = self.get_rect()
            self._overlay_alpha = alpha
            self._overlay = self.build_overlay((rect.width, rect.height), str(text), 255)

    def _hide_overlay(self):
        """Remove any existing overlay.
        """
        self._overlay = None

    def _rotate_image_pil(self, image, rotation):
        """Rotate a PIL image, same direction as RpiCamera.
        """
        if rotation == 90:
            return image.transpose(Image.ROTATE_270)
        if rotation == 180:
            return image.transpose(Image.ROTATE_180)
        if rotation == 270:
            return image.transpose(Image.ROTATE_90)
        return image

    def _get_preview_image(self):
        """Capture a new preview image.
        """
        rect = self.get_rect()
        arr = self._cam.capture_array("main")
        if arr is None:
            raise IOError("Can not get camera preview image")
        if arr.ndim == 3 and arr.shape[2] == 4:
            arr = arr[:, :, :3]
        height, width = arr.shape[:2]
        cropped = sizing.new_size_by_croping_ratio((width, height), self.resolution)
        arr = arr[cropped[1]:cropped[3], cropped[0]:cropped[2], :]
        height, width = arr.shape[:2]
        size = sizing.new_size_keep_aspect_ratio((width, height), (rect.width, rect.height), 'outer')
        pil = Image.fromarray(arr)
        pil = pil.resize((size[0], size[1]), Image.Resampling.LANCZOS)
        pil = self._rotate_image_pil(pil, self.preview_rotation)
        if self.preview_flip:
            pil = pil.transpose(Image.FLIP_LEFT_RIGHT)
        if self._overlay is not None:
            overlay_resized = self._overlay.resize((pil.width, pil.height))
            overlay_resized.putalpha(Image.new('L', overlay_resized.size, self._overlay_alpha))
            pil = pil.convert("RGBA")
            pil = Image.alpha_composite(pil, overlay_resized)
            pil = pil.convert("RGB")
        return pil

    def _post_process_capture(self, capture_data):
        """Rework capture data (BytesIO buffer, effect name) into a PIL Image.
        """
        buffer_stream, effect = capture_data
        buffer_stream.seek(0)
        image = Image.open(buffer_stream).convert("RGB")
        image = self._rotate_image_pil(image, self.capture_rotation)
        image = image.crop(sizing.new_size_by_croping_ratio(image.size, self.resolution))
        image = image.resize(sizing.new_size_keep_aspect_ratio(image.size, self.resolution, 'outer'))
        if self.capture_flip:
            image = image.transpose(Image.FLIP_LEFT_RIGHT)
        if effect != 'none':
            image = image.filter(getattr(ImageFilter, effect.upper()))
        return image

    def preview(self, window, flip=True):
        """Setup the preview.
        """
        self._window = window
        self.preview_flip = flip
        self._window.show_image(self._get_preview_image())

    def preview_countdown(self, timeout, alpha=80):
        """Show a countdown of `timeout` seconds on the preview.
        Returns when the countdown is finished.
        """
        timeout = int(timeout)
        if timeout < 1:
            raise ValueError("Start time shall be greater than 0")
        timer = PoolingTimer(timeout)
        while not timer.is_timeout():
            remaining = int(timer.remaining() + 1)
            if self._overlay is None or remaining != timeout:
                self._show_overlay(str(remaining), alpha)
                timeout = remaining
            updated_rect = self._window.show_image(self._get_preview_image())
            pygame.event.pump()
            if updated_rect:
                pygame.display.update(updated_rect)
        self._show_overlay(get_translated_text('smile'), alpha)
        self._window.show_image(self._get_preview_image())

    def preview_wait(self, timeout, alpha=80):
        """Wait the given time.
        """
        timeout = int(timeout)
        if timeout < 1:
            raise ValueError("Start time shall be greater than 0")
        timer = PoolingTimer(timeout)
        while not timer.is_timeout():
            updated_rect = self._window.show_image(self._get_preview_image())
            pygame.event.pump()
            if updated_rect:
                pygame.display.update(updated_rect)
        self._show_overlay(get_translated_text('smile'), alpha)
        self._window.show_image(self._get_preview_image())

    def stop_preview(self):
        """Stop the preview.
        """
        self._hide_overlay()
        self._window = None

    def capture(self, effect=None):
        """Capture a new picture.
        """
        effect = str(effect).lower()
        if effect not in self.IMAGE_EFFECTS:
            raise ValueError("Invalid capture effect '{}' (choose among {})".format(effect, self.IMAGE_EFFECTS))
        buffer = BytesIO()
        self._cam.switch_mode_and_capture_file(self._still_config, buffer, format="jpeg")
        self._captures.append((buffer, effect))
        time.sleep(0.2)
        self._hide_overlay()

    def quit(self):
        """Close the camera driver, it's definitive.
        """
        if self._cam:
            try:
                self._cam.stop()
            except Exception:
                pass
            self._cam = None
