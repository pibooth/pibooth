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
        # No motorized lens by default, as an IMX219
        self.camera_controls = {}
        self.autofocus_cycles = 0
        self.autofocus_success = True
        self.lens_position = 4.5

    def _new_array(self, size):
        width, height = size
        array = np.zeros((height, width, 4), dtype=np.uint8)
        array[:, :, 0] = np.linspace(0, 255, width, dtype=np.uint8)
        array[:, :, 1] = np.linspace(0, 255, height, dtype=np.uint8)[:, None]
        array[:, :, 2] = 40
        array[:, :, 3] = 255
        return array

    def _new_config(self, main=None, raw=None, controls=None, **kwargs):
        config = {'main': dict(main or {'size': SENSOR_SIZE}), 'controls': dict(controls or {})}
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
        # Switching the mode overwrites the controls with those of the new configuration
        self.config = config
        array = self._new_array(config['main']['size'])
        Image.fromarray(array[:, :, :3]).save(buffer, format=format.upper())

    def autofocus_cycle(self, wait=True):
        assert self.started, "Camera is not started"
        assert 'AfMode' in self.camera_controls, "Camera has no motorized lens"
        self.autofocus_cycles += 1
        return self.autofocus_success

    def capture_metadata(self):
        assert self.started, "Camera is not started"
        if 'AfMode' not in self.camera_controls:
            return {}
        return {'LensPosition': self.lens_position}


class FakeLibcameraControls(object):

    """Minimal stub of the ``libcamera.controls`` module."""

    class AfModeEnum(object):
        Manual = 0
        Auto = 1
        Continuous = 2


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
    monkeypatch.setattr(rpi2, 'libcamera_controls', FakeLibcameraControls)
    cam = rpi2.Rpi2Camera(rpi2.get_rpi2_camera_proxy())
    yield cam
    cam.quit()


@pytest.fixture
def af_camera(camera):
    """Camera with a motorized lens, as the Camera Module 3."""
    camera._cam.camera_controls = {'AfMode': (0, 2, 0), 'LensPosition': (0.0, 32.0, 1.0)}
    return camera


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


def test_autofocus_invalid_mode(camera):
    with pytest.raises(ValueError):
        camera.initialize(100, RESOLUTION, autofocus='auto')


def test_autofocus_ignored_without_motorized_lens(camera):
    camera.initialize(100, RESOLUTION, autofocus='continuous')
    # Nothing to drive on a camera with a fixed lens: no control is forced
    assert camera._preview_config['controls'] == {}
    assert camera._still_config['controls'] == {}
    camera.capture('none')
    assert camera._cam.autofocus_cycles == 0


@pytest.mark.parametrize('mode, expected', [
    ('continuous', {'AfMode': FakeLibcameraControls.AfModeEnum.Continuous}),
    ('capture', {'AfMode': FakeLibcameraControls.AfModeEnum.Auto}),
    ('off', {'AfMode': FakeLibcameraControls.AfModeEnum.Manual, 'LensPosition': 2.5}),
])
def test_autofocus_controls_are_part_of_the_configurations(af_camera, mode, expected):
    af_camera.initialize(100, RESOLUTION, autofocus=mode, lens_position=2.5)
    # Picamera2 overwrites the controls at each (re)configuration, they shall be
    # carried by both configurations to survive a preview resize and a capture
    assert af_camera._preview_config['controls'] == expected
    assert af_camera._still_config['controls'] == expected

    af_camera.preview(FakeWindow(), flip=False)
    assert af_camera._cam.config['controls'] == expected


def test_autofocus_capture_locks_the_lens(af_camera):
    af_camera.initialize(100, RESOLUTION, autofocus='capture')
    af_camera.capture('none')

    # A focus is done on the subject, then the lens is locked so that switching to
    # the still configuration does not start a new focus scan
    assert af_camera._cam.autofocus_cycles == 1
    assert af_camera._still_config['controls'] == {'AfMode': FakeLibcameraControls.AfModeEnum.Manual,
                                                   'LensPosition': af_camera._cam.lens_position}
    assert af_camera._cam.config['controls'] == af_camera._still_config['controls']
    assert af_camera.get_captures()[0].size == RESOLUTION


def test_autofocus_capture_failure_still_captures(af_camera):
    af_camera._cam.autofocus_success = False  # As a scan in front of a blank wall
    af_camera.initialize(100, RESOLUTION, autofocus='capture')
    af_camera.capture('none')
    assert af_camera._cam.autofocus_cycles == 1
    assert af_camera.get_captures()[0].size == RESOLUTION


@pytest.mark.parametrize('mode', ['continuous', 'off'])
def test_autofocus_no_cycle_out_of_the_capture_mode(af_camera, mode):
    af_camera.initialize(100, RESOLUTION, autofocus=mode)
    af_camera.capture('none')
    assert af_camera._cam.autofocus_cycles == 0


def test_autofocus_capture_error_does_not_lose_the_capture(af_camera):
    af_camera.initialize(100, RESOLUTION, autofocus='capture')

    def broken_cycle(wait=True):
        raise RuntimeError("Lens is stuck")

    af_camera._cam.autofocus_cycle = broken_cycle
    af_camera.capture('none')
    assert af_camera.get_captures()[0].size == RESOLUTION
