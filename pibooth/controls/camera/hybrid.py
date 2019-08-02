# -*- coding: utf-8 -*-

from pibooth.controls.camera.rpi import RpiCamera
from pibooth.controls.camera.gphoto import GpCamera


class HybridCamera(RpiCamera):

    """Camera management using the Raspberry Pi camera for the preview (better
    video rendering) and a gPhoto2 compatible camera for the capture (higher
    resolution)
    """

    IMAGE_EFFECTS = GpCamera.IMAGE_EFFECTS

    def __init__(self, *args, **kwargs):
        RpiCamera.__init__(self, *args, **kwargs)
        self._gp_cam = GpCamera(*args, **kwargs)
        self._gp_cam._captures = self._captures  # Same dict for both cameras

    def _post_process_capture(self, capture_path):
        """Rework and return a Image object from file.
        """
        return self._gp_cam._post_process_capture(capture_path)

    def capture(self, filename, effect=None):
        """Capture a picture in a file.
        """
        self._gp_cam.capture(filename, effect)

        self._hide_overlay()  # If stop_preview() has not been called

    def quit(self):
        """Close the camera driver, it's definitive.
        """
        super(HybridCamera, self).quit()
        self._gp_cam.quit()
