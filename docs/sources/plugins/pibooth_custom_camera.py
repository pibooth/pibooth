"""Plugin to handle retry in case of exception with DSLR/gPhoto2 camera."""

import pibooth
from pibooth.utils import LOGGER
from pibooth import camera

__version__ = "4.0.3"


class GpCameraRetry(camera.GpCamera):

    def get_capture_image(self, effect=None):
        """Capture a new picture.
        """
        retry = 0
        max_retry = 2
        while retry < max_retry:
            try:
                return super(GpCameraRetry, self).get_capture_image(effect)
            except Exception:
                LOGGER.warning("Gphoto2 fails to capture, trying again...")
            retry += 1
        raise EnvironmentError("Gphoto2 fails to capture {} times".format(max_retry))


class HybridRpiCameraRetry(camera.HybridRpiCamera):

    def __init__(self, rpi_camera_proxy, gp_camera_proxy):
        super(HybridRpiCameraRetry, self).__init__(rpi_camera_proxy, gp_camera_proxy)
        self._gp_cam = GpCameraRetry(gp_camera_proxy)
        self._gp_cam._captures = self._captures  # Same dict for both cameras


@pibooth.hookimpl
def pibooth_setup_camera():
    rpi_cam_proxy = camera.get_rpi_camera_proxy()
    gp_cam_proxy = camera.get_gp_camera_proxy()

    if rpi_cam_proxy and gp_cam_proxy:
        LOGGER.info("Configuring hybrid camera with retry (Picamera + gPhoto2) ...")
        return HybridRpiCameraRetry(rpi_cam_proxy, gp_cam_proxy)
    elif gp_cam_proxy:
        LOGGER.info("Configuring gPhoto2 camera with retry ...")
        return GpCameraRetry(gp_cam_proxy)
    elif rpi_cam_proxy:
        LOGGER.info("Configuring Picamera camera ...")
        return camera.RpiCamera(rpi_cam_proxy)
