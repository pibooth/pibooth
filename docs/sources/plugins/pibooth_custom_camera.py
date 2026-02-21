"""Plugin to handle retry in case of exception with DSLR/gPhoto2 camera."""

import time
import pibooth
from pibooth.utils import LOGGER
from pibooth import camera

__version__ = "4.0.2"


class GpCameraRetry(camera.GpCamera):

    def capture(self, effect=None):
        """Capture a new picture.
        """
        retry = 0
        max_retry = 2
        while retry < max_retry:
            try:
                return super(GpCameraRetry, self).capture(effect)
            except Exception:
                LOGGER.warning("Gphoto2 fails to capture, trying again...")
            retry += 1
        raise EnvironmentError("Gphoto2 fails to capture {} times".format(max_retry))


class HybridRpi2CameraRetry(camera.HybridRpi2Camera):

    def __init__(self, rpi2_camera_proxy, gp_camera_proxy):
        super(HybridRpi2CameraRetry, self).__init__(rpi2_camera_proxy, gp_camera_proxy)
        self._gp_cam = GpCameraRetry(gp_camera_proxy)
        self._gp_cam._captures = self._captures  # Same list for both cameras


@pibooth.hookimpl
def pibooth_setup_camera(cfg):
    rpi2_cam_proxy = camera.get_rpi2_camera_proxy()
    gp_cam_proxy = camera.get_gp_camera_proxy()

    if rpi2_cam_proxy and gp_cam_proxy:
        LOGGER.info("Configuring hybrid camera with retry (Picamera2 + gPhoto2) ...")
        return HybridRpi2CameraRetry(rpi2_cam_proxy, gp_cam_proxy)
    elif gp_cam_proxy:
        LOGGER.info("Configuring gPhoto2 camera with retry ...")
        return GpCameraRetry(gp_cam_proxy)
    elif rpi2_cam_proxy:
        LOGGER.info("Configuring Picamera2 camera ...")
        return camera.Rpi2Camera(rpi2_cam_proxy)