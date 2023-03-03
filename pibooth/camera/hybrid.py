# -*- coding: utf-8 -*-

from pibooth.camera.rpi import RpiCamera
from pibooth.camera.opencv import CvCamera
from pibooth.camera.gphoto import GpCamera


class HybridRpiCamera(RpiCamera):

    """Camera management using the Raspberry Pi camera for the preview (better
    video rendering) and a gPhoto2 compatible camera for the capture (higher
    resolution)
    """

    IMAGE_EFFECTS = GpCamera.IMAGE_EFFECTS

    def __init__(self, rpi_camera_proxy, gp_camera_proxy):
        super(HybridRpiCamera, self).__init__(rpi_camera_proxy)
        self._gp_cam = GpCamera(gp_camera_proxy)
        self._gp_cam._captures = self._captures  # Same dict for both cameras

    def initialize(self, *args, **kwargs):
        """Ensure that both cameras are initialized.
        """
        super(HybridRpiCamera, self).initialize(*args, **kwargs)
        self._gp_cam.initialize(*args, **kwargs)

    def _post_process_capture(self, capture_data):
        """Rework capture data.

        :param capture_data: couple (GPhotoPath, effect)
        :type capture_data: tuple
        """
        return self._gp_cam._post_process_capture(capture_data)

    def capture(self, effect=None):
        """Capture a picture in a file.
        """
        self._gp_cam.capture(effect)

        self._hide_overlay()  # If stop_preview() has not been called

    def quit(self):
        """Close the camera driver, it's definitive.
        """
        super(HybridRpiCamera, self).quit()
        self._gp_cam.quit()


class HybridCvCamera(CvCamera):

    """Camera management using the OpenCV camera for the preview (better
    video rendering) and a gPhoto2 compatible camera for the capture (higher
    resolution)
    """

    IMAGE_EFFECTS = GpCamera.IMAGE_EFFECTS

    def __init__(self, cv_camera_proxy, gp_camera_proxy):
        super(HybridCvCamera, self).__init__(cv_camera_proxy)
        self._gp_cam = GpCamera(gp_camera_proxy)
        self._gp_cam._captures = self._captures  # Same dict for both cameras

    def initialize(self, *args, **kwargs):
        """Ensure that both cameras are initialized.
        """
        super(HybridCvCamera, self).initialize(*args, **kwargs)
        self._gp_cam.initialize(*args, **kwargs)

    def _post_process_capture(self, capture_data):
        """Rework capture data.

        :param capture_data: couple (GPhotoPath, effect)
        :type capture_data: tuple
        """
        return self._gp_cam._post_process_capture(capture_data)

    def capture(self, effect=None):
        """Capture a picture in a file.
        """
        self._gp_cam.capture(effect)

        self._hide_overlay()  # If stop_preview() has not been called

    def quit(self):
        """Close the camera driver, it's definitive.
        """
        super(HybridCvCamera, self).quit()
        self._gp_cam.quit()
