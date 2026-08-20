# -*- coding: utf-8 -*-

import time
import pygame
from io import BytesIO
try:
    from picamera2 import Picamera2
except Exception as ex:
    # 'picamera2' is optional, it is only available on Raspberry Pi. Note that the
    # import may fail with something else than an 'ImportError' when the package
    # is installed but the 'libcamera' bindings are not usable.
    Picamera2 = None
    PICAMERA2_ERROR = ex
else:
    PICAMERA2_ERROR = None
from PIL import Image, ImageFilter
from pibooth.pictures import sizing
from pibooth.utils import PoolingTimer, LOGGER
from pibooth.language import get_translated_text
from pibooth.camera.base import BaseCamera

MAX_PREVIEW_SIZE = (1280, 720)


def get_rpi2_camera_proxy(port=None):
    """Return camera proxy if a Raspberry Pi camera (libcamera/picamera2) is found
    else return None.

    :param port: look on given camera number
    :type port: int
    """
    if not Picamera2:
        # picamera2 is not installed or can not be loaded
        LOGGER.debug("Picamera2 not available: %s", PICAMERA2_ERROR)
        return None
    try:
        if port is not None:
            cam = Picamera2(port)
        else:
            cam = Picamera2()
        cam.configure(cam.create_preview_configuration())
        cam.start()
        return cam
    except Exception as ex:
        LOGGER.debug("No Raspberry Pi camera detected: %s", ex)
        return None


class Rpi2Camera(BaseCamera):

    """Raspberry Pi camera management, using picamera2 (libcamera).
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
        self._preview_config = None
        self._still_config = None

    def _specific_initialization(self):
        """Camera initialization.
        """
        self._cam.stop()
        # Keep the aspect ratio of the capture resolution for the preview, else the
        # preview would not show what is going to be captured
        preview_size = sizing.new_size_keep_aspect_ratio(self.resolution, MAX_PREVIEW_SIZE)
        self._preview_config = self._cam.create_preview_configuration(
            main={"size": preview_size, "format": "XBGR8888"})
        self._still_config = self._cam.create_still_configuration(main={"size": self.resolution})
        self._cam.configure(self._preview_config)
        self._cam.start()
        LOGGER.debug("Picamera2 configured: preview %s, capture %s", preview_size, self.resolution)

    def _show_overlay(self, text, alpha):
        """Add an image as an overlay.
        """
        if self._window:  # No window means no preview displayed
            rect = self.get_rect()
            self._overlay = self.build_overlay((rect.width, rect.height), str(text), alpha)

    def _rotate_image(self, image, rotation):
        """Rotate a PIL image, same direction than the Raspberry Pi camera.
        """
        if rotation == 90:
            return image.transpose(Image.ROTATE_270)
        elif rotation == 180:
            return image.transpose(Image.ROTATE_180)
        elif rotation == 270:
            return image.transpose(Image.ROTATE_90)
        return image

    def _get_preview_image(self):
        """Capture a new preview image.
        """
        rect = self.get_rect()

        array = self._cam.capture_array("main")
        if array is None:
            raise IOError("Can not get camera preview image")
        # Drop the 4th channel (XBGR8888 gives a RGBX array)
        image = Image.fromarray(array[:, :, :3])
        image = self._rotate_image(image, self.preview_rotation)

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

        :param capture_data: couple (binary data as stream, effect)
        :type capture_data: tuple
        """
        stream, effect = capture_data
        # "Rewind" the stream to the beginning so we can read its content
        stream.seek(0)
        image = Image.open(stream)
        image = self._rotate_image(image, self.capture_rotation)

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
                # Rebuild overlay only if remaining number has changed
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

        stream = BytesIO()
        self._cam.switch_mode_and_capture_file(self._still_config, stream, format='jpeg')
        self._captures.append((stream, effect))
        time.sleep(0.2)  # Necessary to let the camera restart the preview mode

        self._hide_overlay()  # If stop_preview() has not been called

    def quit(self):
        """Close the camera driver, it's definitive.
        """
        if self._cam:
            self._cam.stop()
            self._cam.close()
            self._cam = None
