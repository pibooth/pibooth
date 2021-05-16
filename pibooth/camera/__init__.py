# -*- coding: utf-8 -*-

from pibooth.utils import LOGGER
from pibooth.camera.rpi import RpiCamera, find_rpi_camera
from pibooth.camera.gphoto import GpCamera, find_gp_camera
from pibooth.camera.opencv import CvCamera, find_cv_camera
from pibooth.camera.hybrid import HybridRpiCamera, HybridCvCamera


def _clean(rpi_cam, gp_cam, cv_cam):
    """Close drivers.
    """
    if rpi_cam:
        RpiCamera(rpi_cam).quit()
    if gp_cam:
        GpCamera(gp_cam).quit()
    if cv_cam:
        CvCamera(cv_cam).quit()


def find_camera():
    """Initialize the camera depending of the connected one. The priority order
    is chosen in order to have best rendering during preview and to take captures.
    The gPhoto2 camera is first (drivers most restrictive) to avoid connection
    concurence in case of DSLR compatible with OpenCV.
    """
    rpi_cam = find_rpi_camera()
    gp_cam = find_gp_camera()
    cv_cam = find_cv_camera()

    if rpi_cam and gp_cam:
        LOGGER.info("Configuring hybrid camera (Picamera + gPhoto2) ...")
        _clean(None, None, cv_cam)
        return HybridRpiCamera(rpi_cam, gp_cam)
    elif cv_cam and gp_cam:
        LOGGER.info("Configuring hybrid camera (OpenCV + gPhoto2) ...")
        _clean(rpi_cam, None, None)
        return HybridCvCamera(cv_cam, gp_cam)
    elif gp_cam:
        LOGGER.info("Configuring gPhoto2 camera ...")
        _clean(rpi_cam, None, cv_cam)
        return GpCamera(gp_cam)
    elif rpi_cam:
        LOGGER.info("Configuring Picamera camera ...")
        _clean(None, gp_cam, cv_cam)
        return RpiCamera(rpi_cam)
    elif cv_cam:
        LOGGER.info("Configuring OpenCV camera ...")
        _clean(rpi_cam, gp_cam, None)
        return CvCamera(cv_cam)

    raise EnvironmentError("Neither Raspberry Pi nor GPhoto2 nor OpenCV camera detected")
