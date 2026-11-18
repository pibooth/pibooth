# -*- coding: utf-8 -*-

"""Tests of the Picamera2 backend, running without a Raspberry Pi camera thanks
to a stub of the ``picamera2`` library.
"""

import pytest
import pygame
from PIL import Image, ImageChops
from pibooth import evts
from pibooth import camera as camera_module
from pibooth.camera import rpi2, hybrid
from mocks import camera_drivers

np = pytest.importorskip('numpy')

RESOLUTION = (1934, 2464)  # Portrait, as in the default configuration
WINDOW_RECT = pygame.Rect(0, 0, 800, 480)
SENSOR_SIZE = (1640, 1232)  # Landscape, as a real sensor


class FakePicamera2:

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
        self.capture_error = None

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
        if self.capture_error:
            self.started = False  # As a camera left in the middle of a mode switch
            raise self.capture_error
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


class FakeLibcameraControls:

    """Minimal stub of the ``libcamera.controls`` module."""

    class AfModeEnum:
        Manual = 0
        Auto = 1
        Continuous = 2


@pytest.fixture
def camera(monkeypatch, init_pygame, init_tasks):
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


def start_preview(camera, flip=False):
    """Start the preview and return the first image of the preview task."""
    pygame.event.clear()
    camera.preview(WINDOW_RECT, flip)
    for _ in range(100):
        event = pygame.event.wait(100)
        if event.type == evts.EVT_PIBOOTH_CAM_PREVIEW:
            assert event.exception is None
            return event.result
    raise AssertionError("No preview image received")


def test_no_picamera2_no_proxy(monkeypatch):
    monkeypatch.setattr(rpi2, 'Picamera2', None)
    assert rpi2.get_rpi2_camera_proxy() is None


@pytest.mark.parametrize('rotation', [0, 90, 180, 270])
def test_preview_fits_the_window(camera, rotation):
    camera.initialize(100, RESOLUTION, rotation=rotation)
    image = start_preview(camera)
    # Whatever the rotation, the preview keeps the aspect ratio of the capture
    # resolution and fits in the window
    assert WINDOW_RECT.contains(camera._rect)
    assert image.size == camera._rect.size
    camera.stop_preview()


def test_preview_task_is_stopped(camera):
    camera.initialize(100, RESOLUTION)
    start_preview(camera)
    assert camera._worker.is_alive()
    camera.stop_preview()
    assert camera._worker is None
    # The camera keeps running, ready for the capture
    assert camera._cam.started


def test_preview_flip(camera):
    camera.initialize(100, RESOLUTION)
    camera._rect = WINDOW_RECT
    camera.preview_flip = False
    straight = camera.get_preview_image()
    camera.preview_flip = True
    flipped = camera.get_preview_image()
    assert straight == flipped.transpose(Image.Transpose.FLIP_LEFT_RIGHT)


def test_preview_overlay_only_covers_the_text(camera):
    camera.initialize(100, RESOLUTION)
    camera._rect = WINDOW_RECT
    without_overlay = camera.get_preview_image()
    camera.set_overlay('3', 80)
    with_overlay = camera.get_preview_image()

    diff = ImageChops.difference(without_overlay, with_overlay)
    assert diff.getbbox() is not None, "Overlay is not displayed"
    # Only the text is drawn: the preview itself shall not be darkened
    assert diff.getbbox() != (0, 0, with_overlay.width, with_overlay.height)

    camera.set_overlay(None)
    assert camera.get_preview_image() == without_overlay


def test_capture(camera):
    camera.initialize(100, RESOLUTION)
    camera.capture('none', wait=True)
    images = camera.grab_captures()
    assert len(images) == 1
    assert images[0].size == RESOLUTION
    assert not camera.grab_captures()


def test_capture_stops_the_preview(camera):
    camera.initialize(100, RESOLUTION)
    start_preview(camera)
    preview_config = camera._cam.config
    camera.capture('none', wait=True)
    assert camera._rect is None
    assert camera.grab_captures()[0].size == RESOLUTION
    assert pygame.event.get(evts.EVT_PIBOOTH_CAM_CAPTURE)
    # The preview task is over: no frame is read anymore
    pygame.event.clear()
    pygame.time.wait(100)
    assert not pygame.event.get(evts.EVT_PIBOOTH_CAM_PREVIEW)
    # The next preview does not need to reconfigure the camera
    assert camera._preview_config is preview_config


def test_capture_effect(camera):
    camera.initialize(100, RESOLUTION)
    camera.capture('none', wait=True)
    camera.capture('emboss', wait=True)
    plain, embossed = camera.grab_captures()
    assert ImageChops.difference(plain, embossed).getbbox() is not None


def test_capture_invalid_effect(camera):
    camera.initialize(100, RESOLUTION)
    with pytest.raises(ValueError):
        camera.capture('sepia')


def test_capture_error_is_reported_then_reset(camera):
    camera.initialize(100, RESOLUTION)
    camera._cam.capture_error = RuntimeError("Camera frontend has timed out")
    pygame.event.clear()
    camera.capture('none', wait=True)
    # The failure reaches the main loop through the capture event
    event = pygame.event.get(evts.EVT_PIBOOTH_CAM_CAPTURE)[0]
    assert isinstance(event.exception, RuntimeError)
    assert not camera._cam.started

    # What the failsafe state does: the camera is back in the preview mode
    camera._cam.capture_error = None
    camera.drop_captures()
    camera.reset()
    assert camera._cam.started
    assert camera._cam.config is camera._preview_config
    camera.capture('none', wait=True)
    assert camera.grab_captures()[0].size == RESOLUTION


def test_reset_stops_the_preview(camera):
    camera.initialize(100, RESOLUTION)
    start_preview(camera)
    camera.reset()
    assert camera._worker is None
    assert camera._cam.started


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
    camera.capture('none', wait=True)
    assert camera.grab_captures()[0].size == RESOLUTION


@pytest.mark.parametrize('rotation, expected', [(0, False), (90, True), (180, False), (270, True)])
def test_preview_asks_the_camera_for_the_displayed_size(camera, rotation, expected):
    camera.initialize(100, RESOLUTION, rotation=rotation)
    start_preview(camera)
    rect = camera._rect
    # The ISP delivers the displayed size, no software resize is needed. The size is
    # swapped when the preview is rotated by a quarter turn.
    size = (rect.height, rect.width) if expected else (rect.width, rect.height)
    assert camera._cam.config['main']['size'] == size
    camera.stop_preview()

    # A second preview at the same place does not reconfigure the camera
    config = camera._cam.config
    start_preview(camera)
    assert camera._cam.config is config
    camera.stop_preview()


def test_overlay_is_centered(camera):
    camera.initialize(100, RESOLUTION)
    rect = WINDOW_RECT
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
    camera.capture('none', wait=True)
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

    start_preview(af_camera)
    assert af_camera._cam.config['controls'] == expected
    af_camera.stop_preview()


def test_autofocus_capture_locks_the_lens(af_camera):
    af_camera.initialize(100, RESOLUTION, autofocus='capture')
    af_camera.capture('none', wait=True)

    # A focus is done on the subject, then the lens is locked so that switching to
    # the still configuration does not start a new focus scan
    assert af_camera._cam.autofocus_cycles == 1
    assert af_camera._still_config['controls'] == {'AfMode': FakeLibcameraControls.AfModeEnum.Manual,
                                                   'LensPosition': af_camera._cam.lens_position}
    assert af_camera._cam.config['controls'] == af_camera._still_config['controls']
    assert af_camera.grab_captures()[0].size == RESOLUTION


def test_autofocus_capture_failure_still_captures(af_camera):
    af_camera._cam.autofocus_success = False  # As a scan in front of a blank wall
    af_camera.initialize(100, RESOLUTION, autofocus='capture')
    af_camera.capture('none', wait=True)
    assert af_camera._cam.autofocus_cycles == 1
    assert af_camera.grab_captures()[0].size == RESOLUTION


@pytest.mark.parametrize('mode', ['continuous', 'off'])
def test_autofocus_no_cycle_out_of_the_capture_mode(af_camera, mode):
    af_camera.initialize(100, RESOLUTION, autofocus=mode)
    af_camera.capture('none', wait=True)
    assert af_camera._cam.autofocus_cycles == 0


def test_autofocus_capture_error_does_not_lose_the_capture(af_camera):
    af_camera.initialize(100, RESOLUTION, autofocus='capture')

    def broken_cycle(wait=True):
        raise RuntimeError("Lens is stuck")

    af_camera._cam.autofocus_cycle = broken_cycle
    af_camera.capture('none', wait=True)
    assert af_camera.grab_captures()[0].size == RESOLUTION


# --- Hybrid camera and detection ---------------------------------------------


class FakeCvProxy:

    """Minimal stub of ``cv2.VideoCapture``."""

    released = False

    def release(self):
        self.released = True


@pytest.fixture
def gp_proxy(monkeypatch, captures_portrait):
    from pibooth.camera import gphoto
    monkeypatch.setattr(gphoto, 'gp', camera_drivers.GpCameraProxyMock([]))
    return camera_drivers.GpCameraProxyMock(captures_portrait)


def test_hybrid_previews_with_rpi_and_captures_with_gphoto2(camera, gp_proxy):
    cam = hybrid.HybridRpi2Camera(camera._cam, gp_proxy)
    cam.initialize(100, RESOLUTION)
    image = start_preview(cam)
    assert image.size == cam._rect.size

    cam.capture('none', wait=True)
    assert cam.grab_captures()[0].size == RESOLUTION
    # The Raspberry Pi camera never left the preview mode
    assert cam._cam.config is cam._preview_config
    cam.reset()
    assert cam._cam.started


@pytest.mark.parametrize('rpi, dslr, webcam, expected', [
    (True, True, True, 'HybridRpi2Camera'),
    (True, True, False, 'HybridRpi2Camera'),
    (True, False, True, 'Rpi2Camera'),
    (True, False, False, 'Rpi2Camera'),
    (False, True, True, 'HybridCvCamera'),
    (False, True, False, 'GpCamera'),
    (False, False, True, 'CvCamera'),
])
def test_find_camera(monkeypatch, camera, gp_proxy, rpi, dslr, webcam, expected):
    cv_proxy = FakeCvProxy() if webcam else None
    monkeypatch.setattr(camera_module, 'get_rpi2_camera_proxy', lambda: camera._cam if rpi else None)
    monkeypatch.setattr(camera_module, 'get_gp_camera_proxy', lambda: gp_proxy if dslr else None)
    monkeypatch.setattr(camera_module, 'get_cv_camera_proxy', lambda: cv_proxy)

    cam = camera_module.find_camera()
    assert type(cam).__name__ == expected
    # The cameras left unused are released for the other applications
    if webcam:
        assert cv_proxy.released == (expected in ('HybridRpi2Camera', 'Rpi2Camera'))
    if rpi:
        assert camera._cam.started


def test_find_camera_none(monkeypatch):
    monkeypatch.setattr(camera_module, 'get_rpi2_camera_proxy', lambda: None)
    monkeypatch.setattr(camera_module, 'get_gp_camera_proxy', lambda: None)
    monkeypatch.setattr(camera_module, 'get_cv_camera_proxy', lambda: None)
    with pytest.raises(EnvironmentError):
        camera_module.find_camera()
