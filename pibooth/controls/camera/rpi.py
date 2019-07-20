# -*- coding: utf-8 -*-

import time
import subprocess
import picamera
from pibooth.config.parser import PiConfigParser
from pibooth.controls.camera.base import BaseCamera, LANGUAGES


def rpi_camera_connected():
    """Return True if a RPi camera is found.
    """
    try:
        process = subprocess.Popen(['vcgencmd', 'get_camera'],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, _stderr = process.communicate()
        if stdout and u'detected=1' in stdout.decode('utf-8'):
            return True
    except OSError:
        pass
    return False


class RpiCamera(BaseCamera):

    """Camera management
    """

    IMAGE_EFFECTS = list(picamera.PiCamera.IMAGE_EFFECTS.keys())

    def __init__(self, iso=200, resolution=(1920, 1080), rotation=0, flip=False):
        BaseCamera.__init__(self, resolution)
        self._cam = picamera.PiCamera()
        self._cam.framerate = 15  # Slower is necessary for high-resolution
        self._cam.video_stabilization = True
        self._cam.vflip = False
        self._cam.hflip = flip
        self._cam.resolution = resolution
        self._cam.iso = iso
        self._cam.rotation = rotation

    def _show_overlay(self, text, alpha):
        """Add an image as an overlay.
        """
        if self._window:  # No window means no preview displayed
            rect = self.get_rect()

            # Create an image padded to the required size (required by picamera)
            size = (((rect.width + 31) // 32) * 32, ((rect.height + 15) // 16) * 16)

            image = self.build_overlay(size, str(text), alpha)
            self._overlay = self._cam.add_overlay(image.tobytes(), image.size, layer=3,
                                                  window=tuple(rect), fullscreen=False)

    def _hide_overlay(self):
        """Remove any existing overlay.
        """
        if self._overlay:
            self._cam.remove_overlay(self._overlay)
            self._overlay = None

    def preview(self, window, flip=True):
        """Display a preview on the given Rect (flip if necessary).
        """
        self._window = window
        rect = self.get_rect()
        if self._cam.hflip:
            if flip:
                 # Don't flip again, already done at init
                flip = False
            else:
                # Flip again because flipped once at init
                flip = True
        self._cam.start_preview(resolution=(rect.width, rect.height), hflip=flip,
                                fullscreen=False, window=tuple(rect))

    def preview_countdown(self, timeout, alpha=60):
        """Show a countdown of `timeout` seconds on the preview.
        Returns when the countdown is finished.
        """
        timeout = int(timeout)
        if timeout < 1:
            raise ValueError("Start time shall be greater than 0")
        if not self._cam.preview:
            raise EnvironmentError("Preview shall be started first")

        while timeout > 0:
            self._show_overlay(timeout, alpha)
            time.sleep(1)
            timeout -= 1
            self._hide_overlay()

        self._show_overlay(LANGUAGES.get(PiConfigParser.language, LANGUAGES['en']).get('smile_message'), alpha)

    def preview_wait(self, timeout, alpha=60):
        """Wait the given time.
        """
        time.sleep(timeout)
        self._show_overlay(LANGUAGES.get(PiConfigParser.language, LANGUAGES['en']).get('smile_message'), alpha)

    def stop_preview(self):
        """Stop the preview.
        """
        self._hide_overlay()
        self._cam.stop_preview()
        self._window = None

    def capture(self, filename, effect=None):
        """Capture a picture in a file.
        """
        effect = str(effect).lower()
        if effect not in self.IMAGE_EFFECTS:
            raise ValueError("Invalid capture effect '{}' (choose among {})".format(effect, self.IMAGE_EFFECTS))

        try:
            self._cam.image_effect = effect
            self._cam.capture(filename)
            self._captures[filename] = None  # Nothing to keep for post processing
        finally:
            self._cam.image_effect = 'none'

        self._hide_overlay()  # If stop_preview() has not been called

    def quit(self):
        """Close the camera driver, it's definitive.
        """
        self._cam.close()
