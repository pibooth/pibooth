# -*- coding: utf-8 -*-

import time
import subprocess
from io import BytesIO
from PIL import Image
try:
    import picamera
except ImportError:
    picamera = None  # picamera is optional
from pibooth.language import get_translated_text
from pibooth.camera.base import BaseCamera


def get_rpi_camera_proxy(port=None):
    """Return camera proxy if a Raspberry Pi compatible camera is found
    else return None.

    :param port: look on given port number
    :type port: int
    """
    if not picamera:
        return None  # picamera is not installed
    try:
        process = subprocess.Popen(['vcgencmd', 'get_camera'],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, _stderr = process.communicate()
        if stdout and u'detected=1' in stdout.decode('utf-8'):
            if port is not None:
                return picamera.PiCamera(camera_num=port)
            return picamera.PiCamera()
    except OSError:
        pass
    return None


class RpiCamera(BaseCamera):

    """Camera management
    """

    if picamera:
        IMAGE_EFFECTS = list(picamera.PiCamera.IMAGE_EFFECTS.keys())
    else:
        IMAGE_EFFECTS = []

    def _specific_initialization(self):
        """Camera initialization.
        """
        self._cam.framerate = 15  # Slower is necessary for high-resolution
        self._cam.video_stabilization = True
        self._cam.vflip = False
        self._cam.hflip = self.capture_flip
        self._cam.resolution = self.resolution
        self._cam.iso = self.preview_iso
        self._cam.rotation = self.preview_rotation

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

    def _post_process_capture(self, capture_data):
        """Rework capture data.

        :param capture_data: binary data as stream
        :type capture_data: :py:class:`io.BytesIO`
        """
        # "Rewind" the stream to the beginning so we can read its content
        capture_data.seek(0)
        return Image.open(capture_data)

    def preview(self, window, flip=True):
        """Display a preview on the given Rect (flip if necessary).
        """
        if self._cam.preview is not None:
            # Already running
            return

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

        self._show_overlay(get_translated_text('smile'), alpha)

    def preview_wait(self, timeout, alpha=60):
        """Wait the given time.
        """
        time.sleep(timeout)
        self._show_overlay(get_translated_text('smile'), alpha)

    def stop_preview(self):
        """Stop the preview.
        """
        self._hide_overlay()
        self._cam.stop_preview()
        self._window = None

    def capture(self, effect=None):
        """Capture a new picture in a file.
        """
        effect = str(effect).lower()
        if effect not in self.IMAGE_EFFECTS:
            raise ValueError("Invalid capture effect '{}' (choose among {})".format(effect, self.IMAGE_EFFECTS))

        try:
            if self.capture_iso != self.preview_iso:
                self._cam.iso = self.capture_iso
            if self.capture_rotation != self.preview_rotation:
                self._cam.rotation = self.capture_rotation

            stream = BytesIO()
            self._cam.image_effect = effect
            self._cam.capture(stream, format='jpeg')

            if self.capture_iso != self.preview_iso:
                self._cam.iso = self.preview_iso
            if self.capture_rotation != self.preview_rotation:
                self._cam.rotation = self.preview_rotation

            self._captures.append(stream)
        finally:
            self._cam.image_effect = 'none'

        self._hide_overlay()  # If stop_preview() has not been called

    def quit(self):
        """Close the camera driver, it's definitive.
        """
        self._cam.close()
