# -*- coding: utf-8 -*-

import time
try:
    import cv2
    import numpy as np
except ImportError:
    cv2 = None  # OpenCV is optional
from PIL import Image
from pibooth.pictures import sizing
from pibooth.utils import LOGGER
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

    def _show_overlay(self):
        """Add an image as an overlay.
        """
        pil_image = self.build_overlay((self._rect.width, self._rect.height), self._overlay_text, 255)
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

    def get_preview_image(self):
        """Capture a new preview image.
        """
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
        size = sizing.new_size_keep_aspect_ratio((width, height), (self._rect.width, self._rect.height), 'outer')
        image = cv2.resize(image, size, interpolation=cv2.INTER_AREA)

        if self.preview_flip:
            image = cv2.flip(image, 1)

        if self._overlay is not None:
            if self._overlay.shape != image.shape:
                # Previous operations may create a size with one pixel gap
                self._overlay = cv2.resize(self._overlay, (image.shape[1], image.shape[0]))
            image = cv2.addWeighted(image, 1, self._overlay, self._overlay_alpha / 255., 0)
        return Image.fromarray(image)

    def _process_capture(self, capture_data):
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

    def get_capture_image(self, effect=None):
        """Capture a new picture.
        """
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
        return image

    def _specific_cleanup(self):
        """Close the camera driver, it's definitive.
        """
        if self._cam:
            self._cam.release()
