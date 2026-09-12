# -*- coding: utf-8 -*-

import pygame


def test_cv_preview(camera_cv):
    assert not camera_cv.preview_flip
    assert camera_cv.preview_iso == 100
    assert camera_cv.resolution == (1934, 2464)
    camera_cv.preview(pygame.Rect(0, 0, 800, 480))
    assert camera_cv.preview_flip
    camera_cv.stop_preview()


def test_cv_capture(camera_cv):
    camera_cv.capture(wait=True)
    assert camera_cv.grab_captures()


def test_gp_preview(camera_gp):
    assert not camera_gp.preview_flip
    assert camera_gp.preview_iso == 100
    assert camera_gp.resolution == (1934, 2464)
    camera_gp.preview(pygame.Rect(0, 0, 800, 480))
    assert camera_gp.preview_flip
    camera_gp.stop_preview()


def test_gp_capture(camera_gp):
    camera_gp.capture(wait=True)
    assert camera_gp.grab_captures()


def test_gp_reset(camera_gp):
    camera_gp.preview(pygame.Rect(0, 0, 800, 480))
    camera_gp.reset()
    assert camera_gp._worker is None
    camera_gp.capture(wait=True)
    assert camera_gp.grab_captures()


def test_cv_reset(camera_cv):
    camera_cv.reset()  # Nothing to do for OpenCV
    camera_cv.capture(wait=True)
    assert camera_cv.grab_captures()


def test_hybridc_capture(camera_cv_gp):
    camera_cv_gp.capture(wait=True)
    assert camera_cv_gp.grab_captures()
