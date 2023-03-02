# -*- coding: utf-8 -*-

from pibooth.utils import LOGGER
from pibooth.camera.rpi import RpiCamera, get_rpi_camera_proxy
from pibooth.camera.gphoto import GpCamera, get_gp_camera_proxy
from pibooth.camera.opencv import CvCamera, get_cv_camera_proxy
from pibooth.camera.hybrid import HybridRpiCamera, HybridCvCamera


def close_proxy(rpi_cam_proxy, gp_cam_proxy, cv_cam_proxy):
    """Close proxy drivers.
    """
    if rpi_cam_proxy:
        RpiCamera(rpi_cam_proxy).quit()
    if gp_cam_proxy:
        GpCamera(gp_cam_proxy).quit()
    if cv_cam_proxy:
        CvCamera(cv_cam_proxy).quit()


def find_camera():
    """Initialize the camera depending of the connected one. The priority order
    is chosen in order to have best rendering during preview and to take captures.
    The gPhoto2 camera is first (drivers most restrictive) to avoid connection
    concurence in case of DSLR compatible with OpenCV.
    """
    rpi_cam_proxy = get_rpi_camera_proxy()
    gp_cam_proxy = get_gp_camera_proxy()
    cv_cam_proxy = get_cv_camera_proxy()

    if rpi_cam_proxy and gp_cam_proxy:
        LOGGER.info("Configuring hybrid camera (Picamera + gPhoto2) ...")
        close_proxy(None, None, cv_cam_proxy)
        return HybridRpiCamera(rpi_cam_proxy, gp_cam_proxy)
    elif cv_cam_proxy and gp_cam_proxy:
        LOGGER.info("Configuring hybrid camera (OpenCV + gPhoto2) ...")
        close_proxy(rpi_cam_proxy, None, None)
        return HybridCvCamera(cv_cam_proxy, gp_cam_proxy)
    elif gp_cam_proxy:
        LOGGER.info("Configuring gPhoto2 camera ...")
        close_proxy(rpi_cam_proxy, None, cv_cam_proxy)
        return GpCamera(gp_cam_proxy)
    elif rpi_cam_proxy:
        LOGGER.info("Configuring Picamera camera ...")
        close_proxy(None, gp_cam_proxy, cv_cam_proxy)
        return RpiCamera(rpi_cam_proxy)
    elif cv_cam_proxy:
        LOGGER.info("Configuring OpenCV camera ...")
        close_proxy(rpi_cam_proxy, gp_cam_proxy, None)
        return CvCamera(cv_cam_proxy)

    raise EnvironmentError("Neither Raspberry Pi nor GPhoto2 nor OpenCV camera detected")
