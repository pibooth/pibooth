# -*- coding: utf-8 -*-

from pibooth.utils import LOGGER, pkill
from pibooth.camera.rpi import RpiCamera, rpi_camera_connected
from pibooth.camera.gphoto import GpCamera, gp_camera_connected
from pibooth.camera.opencv import CvCamera, cv_camera_connected
from pibooth.camera.hybrid import HybridRpiCamera, HybridCvCamera


def get_camera(iso, resolution, rotation, flip, delete_internal_memory):
    """Initialize the camera depending of the connected one. If a gPhoto2 camera
    is used, try to kill any process using gPhoto2 as it may block camera access.

    The priority order is chosen in order to have best rendering during preview
    and to take captures.
    """
    if rotation not in (0, 90, 180, 270):
        raise ValueError("Invalid camera rotation value '{}' (should be 0, 90, 180 or 270)".format(rotation))
    if gp_camera_connected() and rpi_camera_connected():
        LOGGER.info("Configuring hybrid camera (Picamera + gPhoto2) ...")
        cam_class = HybridRpiCamera
        pkill('*gphoto2*')
    elif gp_camera_connected() and cv_camera_connected():
        LOGGER.info("Configuring hybrid camera (OpenCV + gPhoto2) ...")
        cam_class = HybridCvCamera
        pkill('*gphoto2*')
    elif gp_camera_connected():
        LOGGER.info("Configuring gPhoto2 camera ...")
        cam_class = GpCamera
        pkill('*gphoto2*')
    elif rpi_camera_connected():
        LOGGER.info("Configuring Picamera camera ...")
        cam_class = RpiCamera
    elif cv_camera_connected():
        LOGGER.info("Configuring OpenCV camera ...")
        cam_class = CvCamera
    else:
        raise EnvironmentError("Neither Raspberry Pi nor GPhoto2 nor OpenCV camera detected")

    return cam_class(iso, resolution, rotation, flip, delete_internal_memory)
