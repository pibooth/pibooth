# -*- coding: utf-8 -*-


import os
import pytest
from PIL import Image
from pibooth import language
from pibooth.counters import Counters
from pibooth.config.parser import PiConfigParser
from pibooth.camera import get_rpi_camera_proxy, get_rpi2_camera_proxy, get_gp_camera_proxy, get_cv_camera_proxy
from pibooth.camera import RpiCamera, Rpi2Camera, GpCamera, CvCamera, HybridRpiCamera, HybridRpi2Camera, HybridCvCamera


ISO = 100
RESOLUTION = (1934, 2464)
MOCKS_DIR = os.path.join(os.path.dirname(__file__), 'mocks')
CAPTURES_DIR = os.path.join(os.path.dirname(__file__), 'captures')


@pytest.fixture
def init(tmpdir):
    return language.init(str(tmpdir.join('translations.cfg')))


@pytest.fixture(scope='session')
def captures_portrait():
    return [Image.open(os.path.join(CAPTURES_DIR, 'portrait', img))
            for img in os.listdir(os.path.join(CAPTURES_DIR, 'portrait'))
            if img.startswith('capture')]


@pytest.fixture(scope='session')
def overlays_portrait_path():
    return [os.path.join(CAPTURES_DIR, 'portrait', img)
            for img in os.listdir(os.path.join(CAPTURES_DIR, 'portrait'))
            if img.startswith('overlay')]


@pytest.fixture(scope='session')
def captures_landscape():
    return [Image.open(os.path.join(CAPTURES_DIR, 'landscape', img))
            for img in os.listdir(os.path.join(CAPTURES_DIR, 'landscape'))
            if img.startswith('capture')]


@pytest.fixture(scope='session')
def overlays_landscape_path():
    return [os.path.join(CAPTURES_DIR, 'landscape', img)
            for img in os.listdir(os.path.join(CAPTURES_DIR, 'landscape'))
            if img.startswith('overlay')]


@pytest.fixture(scope='session')
def fond_path():
    return os.path.join(CAPTURES_DIR, 'fond.jpg')


@pytest.fixture(scope='session')
def cfg_path():
    return os.path.join(MOCKS_DIR, 'pibooth.cfg')


@pytest.fixture(scope='session')
def cfg(cfg_path):
    return PiConfigParser(cfg_path, None)


@pytest.fixture
def counters(tmpdir):
    return Counters(str(tmpdir.join('data.pickle')), nbr_printed=0)


@pytest.fixture(scope='session')
def proxy_rpi():
    return get_rpi_camera_proxy()


@pytest.fixture(scope='session')
def proxy_rpi2():
    return get_rpi2_camera_proxy()


@pytest.fixture(scope='session')
def camera_rpi(proxy_rpi):
    cam = RpiCamera(proxy_rpi)
    cam.initialize(ISO, RESOLUTION, delete_internal_memory=True)
    yield cam
    cam.quit()


@pytest.fixture(scope='session')
def camera_rpi_gp(proxy_rpi, proxy_gp):
    cam = HybridRpiCamera(proxy_rpi, proxy_gp)
    cam.initialize(ISO, RESOLUTION, delete_internal_memory=True)
    yield cam
    cam.quit()


@pytest.fixture(scope='session')
def camera_rpi2(proxy_rpi2):
    if proxy_rpi2 is None:
        pytest.skip("Picamera2 not available")
    cam = Rpi2Camera(proxy_rpi2)
    cam.initialize(ISO, RESOLUTION, delete_internal_memory=True)
    yield cam
    cam.quit()


@pytest.fixture(scope='session')
def camera_rpi2_gp(proxy_rpi2, proxy_gp):
    if proxy_rpi2 is None or proxy_gp is None:
        pytest.skip("Picamera2 and/or gPhoto2 not available")
    cam = HybridRpi2Camera(proxy_rpi2, proxy_gp)
    cam.initialize(ISO, RESOLUTION, delete_internal_memory=True)
    yield cam
    cam.quit()


@pytest.fixture(scope='session')
def proxy_cv():
    return get_cv_camera_proxy()


@pytest.fixture(scope='session')
def camera_cv(proxy_cv):
    cam = CvCamera(proxy_cv)
    cam.initialize(ISO, RESOLUTION, delete_internal_memory=True)
    yield cam
    cam.quit()


@pytest.fixture(scope='session')
def camera_cv_gp(proxy_cv, proxy_gp):
    cam = HybridCvCamera(proxy_cv, proxy_gp)
    cam.initialize(ISO, RESOLUTION, delete_internal_memory=True)
    yield cam
    cam.quit()


@pytest.fixture(scope='session')
def proxy_gp():
    return get_gp_camera_proxy()


@pytest.fixture(scope='session')
def camera_gp(proxy_gp):
    cam = GpCamera(proxy_gp)
    cam.initialize(ISO, RESOLUTION, delete_internal_memory=True)
    yield cam
    cam.quit()
