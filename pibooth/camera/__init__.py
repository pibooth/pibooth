# -*- coding: utf-8 -*-

from pibooth.camera.rpi import RpiCamera, find_rpi_camera
from pibooth.camera.gphoto import GpCamera, find_gp_camera
from pibooth.camera.opencv import CvCamera, find_cv_camera
from pibooth.camera.hybrid import HybridRpiCamera, HybridCvCamera
