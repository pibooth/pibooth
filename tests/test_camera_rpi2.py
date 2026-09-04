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

    The sensor modes are those of an IMX219, where the small and the 1080p ones
    have a reduced field of view.
    """

    SENSOR_MODES = [
        {'size': (640, 480), 'format': 'SRGGB10_CSI2P', 'crop_limits': (1000, 752, 1280, 960)},
        {'size': (1640, 1232), 'format': 'SRGGB10_CSI2P', 'crop_limits': (0, 0, 3280, 2464)},
        {'size': (1920, 1080), 'format': 'SRGGB10_CSI2P', 'crop_limits': (680, 692, 1920, 1080)},
        {'size': (3280, 2464), 'format': 'SRGGB10_CSI2P', 'crop_limits': (0, 0, 3280, 2464)},
    ]

    def __init__(self, camera_num=0):
        self.started = False
        self.config = None
        self.sensor_modes = self.SENSOR_MODES

    def _new_array(self, size):
        width, height = size
        array = np.zeros((height, width, 4), dtype=np.uint8)
        array[:, :, 0] = np.linspace(0, 255, width, dtype=np.uint8)
        array[:, :, 1] = np.linspace(0, 255, height, dtype=np.uint8)[:, None]
        array[:, :, 2] = 40
        array[:, :, 3] = 255
        return array

    def _new_config(self, main=None, raw=None, **kwargs):
        config = {'main': dict(main or {'size': SENSOR_SIZE})}
        if raw is not None:
            config['raw'] = dict(raw)
        return config

    create_preview_configuration = _new_config
    create_still_configuration = _new_config

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


def test_sensor_modes_share_the_same_field_of_view(camera):
    camera.initialize(100, RESOLUTION)
    # The modes with a reduced field of view are not eligible, the smallest of the
    # remaining ones is used for the preview and the biggest one for the capture
    assert camera._preview_mode['size'] == (1640, 1232)
    assert camera._capture_mode['size'] == (3280, 2464)
    assert camera._preview_mode['crop_limits'] == camera._capture_mode['crop_limits']
    assert camera._still_config['raw']['size'] == (3280, 2464)
    assert camera._preview_config['raw']['size'] == (1640, 1232)


def test_sensor_modes_not_readable(camera):
    camera._cam.sensor_modes = None  # As picamera2 would do if it can not report them
    camera.initialize(100, RESOLUTION)
    # No sensor mode is forced, but the camera stays usable
    assert camera._preview_mode is None
    assert 'raw' not in camera._still_config
    camera.capture('none')
    assert camera.get_captures()[0].size == RESOLUTION


@pytest.mark.parametrize('rotation, expected', [(0, False), (90, True), (180, False), (270, True)])
def test_preview_asks_the_camera_for_the_displayed_size(camera, rotation, expected):
    camera.initialize(100, RESOLUTION, rotation=rotation)
    window = FakeWindow()
    camera.preview(window, flip=False)
    rect = camera.get_rect()
    # The ISP delivers the displayed size, no software resize is needed. The size is
    # swapped when the preview is rotated by a quarter turn.
    size = (rect.height, rect.width) if expected else (rect.width, rect.height)
    assert camera._cam.config['main']['size'] == size

    # A second preview on the same window does not reconfigure the camera
    config = camera._cam.config
    camera.preview(window, flip=False)
    assert camera._cam.config is config


def test_overlay_is_centered(camera):
    camera.initialize(100, RESOLUTION)
    camera._window = FakeWindow()
    rect = camera.get_rect()
    overlay = camera.build_overlay((rect.width, rect.height), '3', 255)
    left, top, right, bottom = overlay.getbbox()
    assert abs((left + right) / 2 - rect.width / 2) < 0.05 * rect.width
    assert abs((top + bottom) / 2 - rect.height / 2) < 0.05 * rect.height
