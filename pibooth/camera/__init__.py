# -*- coding: utf-8 -*-

from pibooth.utils import LOGGER
from pibooth.camera.rpi import RpiCamera, find_rpi_camera
from pibooth.camera.gphoto import GpCamera, find_gp_camera
from pibooth.camera.opencv import CvCamera, find_cv_camera
from pibooth.camera.hybrid import HybridRpiCamera, HybridCvCamera


def get_camera(iso, resolution, rotation, flip, delete_internal_memory):
    """Initialize the camera depending of the connected one. If a gPhoto2 camera
    is used, try to kill any process using gPhoto2 as it may block camera access.

    The priority order is chosen in order to have best rendering during preview
    and to take captures.
    """
    if rotation not in (0, 90, 180, 270):
        raise ValueError("Invalid camera rotation value '{}' (should be 0, 90, 180 or 270)".format(rotation))

    # Initialize the gPhoto2 camera first (drivers most restrictive) to avoid
    # connection concurence in case of DSLR compatible with OpenCV.
    rpi_cam = find_rpi_camera()
    gp_cam = find_gp_camera()
    cv_cam = find_cv_camera()

    if rpi_cam and gp_cam:
        LOGGER.info("Configuring hybrid camera (Picamera + gPhoto2) ...")
        camera = HybridRpiCamera(rpi_cam, gp_cam)
    elif cv_cam and gp_cam:
        LOGGER.info("Configuring hybrid camera (OpenCV + gPhoto2) ...")
        camera = HybridCvCamera(cv_cam, gp_cam)
    elif gp_cam:
        LOGGER.info("Configuring gPhoto2 camera ...")
        camera = GpCamera(gp_cam)
    elif rpi_cam:
        LOGGER.info("Configuring Picamera camera ...")
        camera = RpiCamera(rpi_cam)
    elif cv_cam:
        LOGGER.info("Configuring OpenCV camera ...")
        camera = CvCamera(cv_cam)
    else:
        raise EnvironmentError("Neither Raspberry Pi nor GPhoto2 nor OpenCV camera detected")

    camera.initialize(iso, resolution, rotation, flip, delete_internal_memory)
    return camera
