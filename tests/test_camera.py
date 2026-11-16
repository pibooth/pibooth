# -*- coding: utf-8 -*-

import pytest
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
    camera_cv.reset()
    camera_cv.capture(wait=True)
    assert camera_cv.grab_captures()


def test_hybridc_capture(camera_cv_gp):
    camera_cv_gp.capture(wait=True)
    assert camera_cv_gp.grab_captures()


def test_cv_preview_tolerates_failed_reads(camera_cv):
    """A webcam may not deliver the first frames after a change of resolution."""
    camera_cv._rect = pygame.Rect(0, 0, 800, 480)
    camera_cv._cam.failures = camera_cv.READ_ATTEMPTS - 1
    assert camera_cv.get_preview_image()
    camera_cv._rect = None


def test_cv_preview_fails_if_no_frame(camera_cv):
    camera_cv._rect = pygame.Rect(0, 0, 800, 480)
    camera_cv._cam.failures = camera_cv.READ_ATTEMPTS
    with pytest.raises(IOError):
        camera_cv.get_preview_image()
    camera_cv._rect = None


def test_cv_reset_reopens_a_stuck_webcam(camera_cv):
    """Issue #697: after a capture, the webcam does not deliver frames anymore.
    The failsafe state resets the camera, which shall make it work again."""
    camera_cv._cam.broken = True
    camera_cv.capture(wait=True)
    assert not camera_cv.grab_captures()
    with pytest.raises(IOError):
        camera_cv._rect = pygame.Rect(0, 0, 800, 480)
        camera_cv.get_preview_image()

    camera_cv.reset()
    assert camera_cv._cam.opened_ports[-1] == 0
    camera_cv._rect = pygame.Rect(0, 0, 800, 480)  # Dropped by the reset
    assert camera_cv.get_preview_image()
    camera_cv._rect = None
    camera_cv.capture(wait=True)
    assert camera_cv.grab_captures()
