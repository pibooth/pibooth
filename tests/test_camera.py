# -*- coding: utf-8 -*-


def test_rpi_capture(camera_rpi):
    camera_rpi.capture(wait=True)
    assert camera_rpi.grab_captures()


def test_cv_capture(camera_cv):
    camera_cv.capture(wait=True)
    assert camera_cv.grab_captures()


def test_gp_capture(camera_gp):
    camera_gp.capture(wait=True)
    assert camera_gp.grab_captures()


def test_hybridr_capture(camera_rpi_gp):
    camera_rpi_gp.capture(wait=True)
    assert camera_rpi_gp.grab_captures()


def test_hybridc_capture(camera_cv_gp):
    camera_cv_gp.capture(wait=True)
    assert camera_cv_gp.grab_captures()
