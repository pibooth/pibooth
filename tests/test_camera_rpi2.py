# -*- coding: utf-8 -*-

"""Tests of the Picamera2 backend, running without a Raspberry Pi camera thanks
to a stub of the ``picamera2`` library.
"""

import pytest
import pygame
from PIL import Image, ImageChops
from pibooth.camera import rpi2

np = pytest.importorskip('numpy')

RESOLUTION = (1934, 2464)  # Portrait, as in the default configuration
SENSOR_SIZE = (1640, 1232)  # Landscape, as a real sensor


class FakePicamera2(object):

    """Minimal stub of ``picamera2.Picamera2``: it delivers a gradient image
    in the XBGR8888 format (as the real preview configuration does).
    """

    def __init__(self, camera_num=0):
        self.started = False
        self.config = None

    def _new_array(self, size):
        width, height = size
        array = np.zeros((height, width, 4), dtype=np.uint8)
        array[:, :, 0] = np.linspace(0, 255, width, dtype=np.uint8)
        array[:, :, 1] = np.linspace(0, 255, height, dtype=np.uint8)[:, None]
        array[:, :, 2] = 40
        array[:, :, 3] = 255
        return array

    def create_preview_configuration(self, main=None, **kwargs):
        return {'main': dict(main or {'size': SENSOR_SIZE})}

    def create_still_configuration(self, main=None, **kwargs):
        return {'main': dict(main or {'size': SENSOR_SIZE})}

    def configure(self, config):
        self.config = config

    def start(self):
        self.started = True

    def stop(self):
        self.started = False

    def close(self):
        self.started = False

    def capture_array(self, name="main"):
        assert self.started, "Camera is not started"
        return self._new_array(self.config['main']['size'])

    def switch_mode_and_capture_file(self, config, buffer, format="jpeg"):
        assert self.started, "Camera is not started"
        array = self._new_array(config['main']['size'])
        Image.fromarray(array[:, :, :3]).save(buffer, format=format.upper())


class FakeWindow(object):

    """Minimal stub of :py:class:`PiWindow` (no display required)."""

    def __init__(self, size=(800, 480)):
        self._rect = pygame.Rect(0, 0, size[0], size[1])
        self.image = None

    def get_rect(self, absolute=False):
        return self._rect

    def show_image(self, image):
        self.image = image
        return None


@pytest.fixture
def camera(monkeypatch):
    monkeypatch.setattr(rpi2, 'Picamera2', FakePicamera2)
    monkeypatch.setattr(rpi2, 'PICAMERA2_ERROR', None)
    cam = rpi2.Rpi2Camera(rpi2.get_rpi2_camera_proxy())
    yield cam
    cam.quit()


def test_no_picamera2_no_proxy(monkeypatch):
    monkeypatch.setattr(rpi2, 'Picamera2', None)
    assert rpi2.get_rpi2_camera_proxy() is None


@pytest.mark.parametrize('rotation', [0, 90, 180, 270])
def test_preview_fits_the_window(camera, rotation):
    camera.initialize(100, RESOLUTION, rotation=rotation)
    window = FakeWindow()
    camera.preview(window, flip=False)
    # Whatever the rotation, the preview keeps the aspect ratio of the capture
    # resolution and fits in the window
    rect = camera.get_rect()
    assert window.image.size == (rect.width, rect.height)


def test_preview_flip(camera):
    camera.initialize(100, RESOLUTION)
    camera._window = FakeWindow()
    camera.preview_flip = False
    straight = camera._get_preview_image()
    camera.preview_flip = True
    flipped = camera._get_preview_image()
    assert straight == flipped.transpose(Image.FLIP_LEFT_RIGHT)


def test_preview_overlay_only_covers_the_text(camera):
    camera.initialize(100, RESOLUTION)
    camera._window = FakeWindow()
    without_overlay = camera._get_preview_image()
    camera._show_overlay('3', 80)
    with_overlay = camera._get_preview_image()

    diff = ImageChops.difference(without_overlay, with_overlay)
    assert diff.getbbox() is not None, "Overlay is not displayed"
    # Only the text is drawn: the preview itself shall not be darkened
    assert diff.getbbox() != (0, 0, with_overlay.width, with_overlay.height)

    camera._hide_overlay()
    assert camera._get_preview_image() == without_overlay


def test_capture(camera):
    camera.initialize(100, RESOLUTION)
    camera.capture('none')
    images = camera.get_captures()
    assert len(images) == 1
    assert images[0].size == RESOLUTION
    assert not camera.get_captures()


def test_capture_invalid_effect(camera):
    camera.initialize(100, RESOLUTION)
    with pytest.raises(ValueError):
        camera.capture('sepia')


def test_quit(camera):
    camera.initialize(100, RESOLUTION)
    camera.quit()
    assert camera._cam is None
