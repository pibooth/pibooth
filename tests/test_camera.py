# -*- coding: utf-8 -*-

import os
import pytest


@pytest.mark.skipif("CAM_VIDEODRIVER" in os.environ, reason="No camera")
def test_rpi_capture(camera_rpi):
    camera_rpi.capture()
    assert camera_rpi.get_captures()


@pytest.mark.skipif("CAM_VIDEODRIVER" in os.environ, reason="No camera")
def test_cv_capture(camera_cv):
    camera_cv.capture()
    assert camera_cv.get_captures()


@pytest.mark.skipif("CAM_VIDEODRIVER" in os.environ, reason="No camera")
def test_gp_capture(camera_gp):
    camera_gp.capture()
    assert camera_gp.get_captures()


@pytest.mark.skipif("CAM_VIDEODRIVER" in os.environ, reason="No camera")
def test_hybridr_capture(camera_rpi_gp):
    camera_rpi_gp.capture()
    assert camera_rpi_gp.get_captures()


@pytest.mark.skipif("CAM_VIDEODRIVER" in os.environ, reason="No camera")
def test_hybridc_capture(camera_cv_gp):
    camera_cv_gp.capture()
    assert camera_cv_gp.get_captures()
