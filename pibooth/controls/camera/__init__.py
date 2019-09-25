# -*- coding: utf-8 -*-

from pibooth.utils import LOGGER, pkill
from pibooth.controls.camera.rpi import RpiCamera, rpi_camera_connected
from pibooth.controls.camera.gphoto import GpCamera, gp_camera_connected
from pibooth.controls.camera.gphoto_omx import GpOmxCamera, gpomx_camera_connected
from pibooth.controls.camera.opencv import CvCamera, cv_camera_connected
from pibooth.controls.camera.hybrid import HybridCamera


def get_camera(iso, resolution, rotation, flip, delete_internal_memory):
    """Initialize the camera depending of the connected one. If a gPhoto2 camera
    is used, try to kill any process using gPhoto2 as it may block camera access.

    The priority order is chosen in order to have best rendering during preview
    and to take captures.
    """
    if gp_camera_connected() and rpi_camera_connected():
        LOGGER.info("Configuring hybrid camera (Picamera + gPhoto2) ...")
        cam_class = HybridCamera
        pkill('*gphoto2*')
    elif gpomx_camera_connected():
        LOGGER.info("Configuring gPhoto2 camera (preview with OMXPlayer) ...")
        cam_class = GpOmxCamera
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
