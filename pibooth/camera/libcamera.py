# -*- coding: utf-8 -*-

import time
import pygame
try:
    import libcamera
except ImportError:
    libcamera = None  # libcamera is optional
from PIL import Image, ImageFilter
from pibooth.pictures import sizing
from pibooth.utils import PoolingTimer, LOGGER
from pibooth.language import get_translated_text
from pibooth.camera.base import BaseCamera


def get_libcamera_camera_proxy(port=None):
    """Return camera proxy if a Raspberry Pi compatible camera is found
    else return None.

    :param port: look on given port number
    :type port: int
    """
    if not libcamera:
        return None  # libcamera is not installed
    try:
        if port is not None:
            return libcamera.libcamera(camera_num=port)
        return libcamera.libcamera()
    except OSError:
        pass
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
        super(LibCamera, self).__init__(camera_proxy)
        self._overlay_alpha = 255

    def _specific_initialization(self):
        """Camera initialization.
        """
        # It seems that cameras are always in landscape
        self._cam.initCamera(max(self.resolution), min(self.resolution),
                             libcamera.PixelFormat.BGR888, buffercount=4,
                             rotation=self.preview_rotation)
        self._cam.startCamera()
        framerate = 30
        frame_time = 1000000 // framerate
        self._cam.set(libcamera.FrameDurationLimits, [frame_time, frame_time])
        self._cam.set(libcamera.ExposureTime, self.preview_iso)

    def _show_overlay(self, text, alpha):
        """Add an image as an overlay.
        """
        if self._window:  # No window means no preview displayed
            rect = self.get_rect()
            self._overlay_alpha = alpha
            self._overlay = self.build_overlay((rect.width, rect.height), str(text), alpha)

    def _get_preview_image(self):
        """Capture a new preview image.
        """
        rect = self.get_rect()

        ret, data = self._cam.readFrame()
        if not ret:
            raise IOError("Can not get camera preview image")
        image = Image.fromarray(data.imageData)

        self._cam.returnFrameBuffer(data)
        # Crop to keep aspect ratio of the resolution
        image = image.crop(sizing.new_size_by_croping_ratio(image.size, self.resolution))
        # Resize to fit the available space in the window
        image = image.resize(sizing.new_size_keep_aspect_ratio(image.size, (rect.width, rect.height), 'outer'))

        if self.preview_flip:
            image = image.transpose(Image.FLIP_LEFT_RIGHT)

        if self._overlay:
            image.paste(self._overlay, (0, 0), self._overlay)
        return image

    def _post_process_capture(self, capture_data):
        """Rework capture data.

        :param capture_data: couple (frame, effect)
        :type capture_data: tuple
        """
        frame, effect = capture_data
        image = Image.fromarray(frame)

        # Crop to keep aspect ratio of the resolution
        image = image.crop(sizing.new_size_by_croping_ratio(image.size, self.resolution))
        # Resize to fit the resolution
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
                # Rebluid overlay only if remaining number has changed
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

        if self.capture_iso != self.preview_iso:
            self._cam.set(libcamera.ExposureTime, self.capture_iso)

        LOGGER.debug("Taking capture at resolution %s", self.resolution)
        ret, data = self._cam.readFrame()
        if not ret:
            raise IOError("Can not capture frame")

        if self.capture_iso != self.preview_iso:
            self._cam.set(libcamera.ExposureTime, self.preview_iso)

        self._captures.append((data.imageData, effect))
        self._cam.returnFrameBuffer(data)
        time.sleep(0.5)  # To let time to see "Smile"

        self._hide_overlay()  # If stop_preview() has not been called

    def quit(self):
        """Close the camera driver, it's definitive.
        """
        if self._cam:
            self._cam.stopCamera()
            self._cam.closeCamera()
