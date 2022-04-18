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

    def _process_capture(self, capture_data):
        """Rework capture data.

        :param capture_data: couple (GPhotoPath, effect)
        :type capture_data: tuple
        """
        return self._gp_cam._process_capture(capture_data)

    def get_capture_image(self, effect=None):
        """Capture a picture in a file.
        """
        return self._gp_cam.get_capture_image(effect)

    def _specific_cleanup(self):
        """Ensure that both cameras are cleaned.
        """
        super(HybridRpiCamera, self)._specific_cleanup()
        self._gp_cam._specific_cleanup()


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

    def _process_capture(self, capture_data):
        """Rework capture data.

        :param capture_data: couple (GPhotoPath, effect)
        :type capture_data: tuple
        """
        return self._gp_cam._process_capture(capture_data)

    def get_capture_image(self, effect=None):
        """Capture a picture in a file.
        """
        return self._gp_cam.get_capture_image(effect)

    def _specific_cleanup(self):
        """Ensure that both cameras are cleaned.
        """
        super(HybridCvCamera, self)._specific_cleanup()
        self._gp_cam._specific_cleanup()
