# -*- coding: utf-8 -*-

import pygame


def test_rpi_preview(camera_rpi):
    assert not camera_rpi.preview_flip
    assert camera_rpi.preview_iso == 100
    assert camera_rpi.resolution == (1934, 2464)
    camera_rpi.preview(pygame.Rect(0, 0, 800, 480))
    assert camera_rpi.preview_flip
    camera_rpi.stop_preview()


def test_rpi_capture(camera_rpi):
    camera_rpi.capture(wait=True)
    assert camera_rpi.grab_captures()


def test_libcamera_preview(camera_libcamera):
    assert not camera_libcamera.preview_flip
    assert camera_libcamera.preview_iso == 100
    assert camera_libcamera.resolution == (1934, 2464)
    camera_libcamera.preview(pygame.Rect(0, 0, 800, 480))
    assert camera_libcamera.preview_flip
    camera_libcamera.stop_preview()


def test_libcamera_capture(camera_libcamera):
    camera_libcamera.capture(wait=True)
    assert camera_libcamera.grab_captures()


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


def test_hybridr_capture(camera_rpi_gp):
    camera_rpi_gp.capture(wait=True)
    assert camera_rpi_gp.grab_captures()


def test_hybridl_capture(camera_libcamera_gp):
    camera_libcamera_gp.capture(wait=True)
    assert camera_libcamera_gp.grab_captures()


def test_hybridc_capture(camera_cv_gp):
    camera_cv_gp.capture(wait=True)
    assert camera_cv_gp.grab_captures()
