# -*- coding: utf-8 -*-

from pibooth.utils import LOGGER
from pibooth.camera.gphoto import GpCamera, get_gp_camera_proxy
from pibooth.camera.opencv import CvCamera, get_cv_camera_proxy
from pibooth.camera.hybrid import HybridCvCamera


def close_proxy(gp_cam_proxy, cv_cam_proxy):
    """Close proxy drivers.
    """
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
    gp_cam_proxy = get_gp_camera_proxy()
    cv_cam_proxy = get_cv_camera_proxy()

    if cv_cam_proxy and gp_cam_proxy:
        LOGGER.info("Configuring hybrid camera (OpenCV + gPhoto2) ...")
        return HybridCvCamera(cv_cam_proxy, gp_cam_proxy)
    if gp_cam_proxy:
        LOGGER.info("Configuring gPhoto2 camera ...")
        close_proxy(None, cv_cam_proxy)
        return GpCamera(gp_cam_proxy)
    if cv_cam_proxy:
        LOGGER.info("Configuring OpenCV camera ...")
        close_proxy(gp_cam_proxy, None)
        return CvCamera(cv_cam_proxy)

    raise EnvironmentError("Neither gPhoto2 nor OpenCV camera detected")
