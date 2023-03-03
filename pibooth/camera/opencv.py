# -*- coding: utf-8 -*-

import time
import pygame
try:
    import cv2
    import numpy as np
except ImportError:
    cv2 = None  # OpenCV is optional
from PIL import Image
from pibooth.pictures import sizing
from pibooth.utils import PoolingTimer, LOGGER
from pibooth.language import get_translated_text
from pibooth.camera.base import BaseCamera


def get_cv_camera_proxy(port=None):
    """Return camera proxy if an OpenCV compatible camera is found
    else return None.

    :param port: look on given port number
    :type port: int
    """
    if not cv2:
        return None  # OpenCV is not installed

    if port is not None:
        if not isinstance(port, int):
            raise TypeError("Invalid OpenCV camera port '{}'".format(type(port)))
        camera = cv2.VideoCapture(port)
        if camera.isOpened():
            return camera
    else:
        for i in range(3):  # Test 3 first ports
            camera = cv2.VideoCapture(i)
            if camera.isOpened():
                return camera

    return None


class CvCamera(BaseCamera):

    """OpenCV camera management.
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
        super(CvCamera, self).__init__(camera_proxy)
        self._overlay_alpha = 255
        self._preview_resolution = None

    def _specific_initialization(self):
        """Camera initialization.
        """
        self._preview_resolution = (self._cam.get(cv2.CAP_PROP_FRAME_WIDTH), self._cam.get(cv2.CAP_PROP_FRAME_HEIGHT))
        LOGGER.debug("Preview resolution is %s", self._preview_resolution)
        self._cam.set(cv2.CAP_PROP_ISO_SPEED, self.preview_iso)

    def _show_overlay(self, text, alpha):
        """Add an image as an overlay.
        """
        if self._window:  # No window means no preview displayed
            rect = self.get_rect()
            self._overlay_alpha = alpha
            pil_image = self.build_overlay((rect.width, rect.height), str(text), 255)
            # Remove alpha from overlay
            self._overlay = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGBA2RGB)

    def _rotate_image(self, image, rotation):
        """Rotate an OpenCV image, same direction than RpiCamera.
        """
        if rotation == 90:
            image = cv2.transpose(image)
            return cv2.flip(image, 1)
        elif rotation == 180:
            return cv2.flip(image, -1)
        elif rotation == 270:
            image = cv2.transpose(image)
            return cv2.flip(image, 0)
        return image

    def _get_preview_image(self):
        """Capture a new preview image.
        """
        rect = self.get_rect()

        ret, image = self._cam.read()
        if not ret:
            raise IOError("Can not get camera preview image")
        image = self._rotate_image(image, self.preview_rotation)

        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        # Crop to keep aspect ratio of the resolution
        height, width = image.shape[:2]
        cropped = sizing.new_size_by_croping_ratio((width, height), self.resolution)
        image = image[cropped[1]:cropped[3], cropped[0]:cropped[2]]
        # Resize to fit the available space in the window
        height, width = image.shape[:2]
        size = sizing.new_size_keep_aspect_ratio((width, height), (rect.width, rect.height), 'outer')
        image = cv2.resize(image, size, interpolation=cv2.INTER_AREA)

        if self.preview_flip:
            image = cv2.flip(image, 1)

        if self._overlay is not None:
            if self._overlay.shape != image.shape:
                # Previous operations may create a size with one pixel gap
                self._overlay = cv2.resize(self._overlay, (image.shape[1], image.shape[0]))
            image = cv2.addWeighted(image, 1, self._overlay, self._overlay_alpha / 255., 0)
        return Image.fromarray(image)

    def _post_process_capture(self, capture_data):
        """Rework capture data.

        :param capture_data: couple (frame, effect)
        :type capture_data: tuple
        """
        frame, effect = capture_data

        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Crop to keep aspect ratio of the resolution
        height, width = image.shape[:2]
        cropped = sizing.new_size_by_croping_ratio((width, height), self.resolution)
        image = image[cropped[1]:cropped[3], cropped[0]:cropped[2]]
        # Resize to fit the resolution
        height, width = image.shape[:2]
        size = sizing.new_size_keep_aspect_ratio((width, height), self.resolution, 'outer')
        image = cv2.resize(image, size, interpolation=cv2.INTER_AREA)

        if self.capture_flip:
            image = cv2.flip(image, 1)

        if effect != 'none':
            LOGGER.warning("Effect with OpenCV camera is not implemented")

        return Image.fromarray(image)

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

        self._cam.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
        self._cam.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])

        if self.capture_iso != self.preview_iso:
            self._cam.set(cv2.CAP_PROP_ISO_SPEED, self.capture_iso)

        LOGGER.debug("Taking capture at resolution %s", self.resolution)
        ret, image = self._cam.read()
        if not ret:
            raise IOError("Can not capture frame")
        image = self._rotate_image(image, self.capture_rotation)

        LOGGER.debug("Putting preview resolution back to %s", self._preview_resolution)
        self._cam.set(cv2.CAP_PROP_FRAME_WIDTH, self._preview_resolution[0])
        self._cam.set(cv2.CAP_PROP_FRAME_HEIGHT, self._preview_resolution[1])

        if self.capture_iso != self.preview_iso:
            self._cam.set(cv2.CAP_PROP_ISO_SPEED, self.preview_iso)

        self._captures.append((image, effect))
        time.sleep(0.5)  # To let time to see "Smile"

        self._hide_overlay()  # If stop_preview() has not been called

    def quit(self):
        """Close the camera driver, it's definitive.
        """
        if self._cam:
            self._cam.release()
