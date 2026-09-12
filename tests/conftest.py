# -*- coding: utf-8 -*-


import os
import pygame
from PIL import Image
from pibooth import language
from pibooth.tasks import AsyncTasksPool
from pibooth.counters import Counters
from pibooth.printer import Printer
from pibooth.config.parser import PiboothConfigParser
from pibooth.plugins import create_plugin_manager
from pibooth.view import get_scene
from pibooth.view.pygame import sprites
from pibooth.camera import get_gp_camera_proxy, get_cv_camera_proxy
from pibooth.camera import GpCamera, CvCamera, HybridCvCamera

# Modules for tests purpose
import pytest
from mocks import camera_drivers, printer_drivers


ISO = 100
RESOLUTION = (1934, 2464)
MOCKS_DIR = os.path.join(os.path.dirname(__file__), 'mocks')
CAPTURES_DIR = os.path.join(os.path.dirname(__file__), 'captures')


# --- Resources ---------------------------------------------------------------

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
def plugin_path():
    return os.path.join(MOCKS_DIR, 'testplugin.py')


@pytest.fixture
def cfg_path(tmpdir):
    tmpfile = tmpdir.join("test_pibooth_config.cfg")
    # Create a dummy configuration file in a temporary directory
    with open(os.path.join(MOCKS_DIR, 'pibooth.cfg')) as fp:
        tmpfile.write(fp.read())
    return str(tmpfile)


# --- Pibooth initialization --------------------------------------------------

@pytest.fixture
def init_lang(tmpdir):
    return language.init(str(tmpdir.join('translations.cfg')))


@pytest.fixture(scope='session')
def init_pygame():
    pygame.init()
    pygame.display.set_caption("Hit [ESC] to end the test")
    yield pygame.display.set_mode((400, 400), pygame.RESIZABLE)
    pygame.quit()


@pytest.fixture(scope='session')
def init_tasks():
    pool = AsyncTasksPool()
    yield pool
    pool.quit()


@pytest.fixture
def pm():
    return create_plugin_manager()


@pytest.fixture
def cfg(cfg_path, pm):
    config = PiboothConfigParser(cfg_path, pm)
    # Update autostart location to a temporary directory
    config.autostart_filename = os.path.dirname(cfg_path) + "/autostart"
    return config


@pytest.fixture
def counters(tmpdir):
    return Counters(str(tmpdir.join('data.json')), nbr_printed=0)


# --- Printer -----------------------------------------------------------------


@pytest.fixture
def cups_conn(monkeypatch):
    """Replace the CUPS binding of the printer module by a fake connection
    with one idle printer. No CUPS server is needed.
    """
    conn = printer_drivers.CupsConnectionMock(
        printers={'fake-printer': {'printer-state': printer_drivers.PRINTER_STATE_IDLE,
                                   'printer-state-reasons': [],
                                   'printer-state-message': ''}},
        default='fake-printer')
    monkeypatch.setattr('pibooth.printer.cups', printer_drivers.CupsModuleMock(conn))
    monkeypatch.setattr('pibooth.printer.Subscriber', printer_drivers.CupsSubscriberMock, raising=False)
    monkeypatch.setattr('pibooth.printer.event', printer_drivers.CupsEventMock, raising=False)
    return conn


@pytest.fixture
def printer(cups_conn):
    printer = Printer()
    yield printer
    printer.quit()


# --- Window events loop ------------------------------------------------------


@pytest.fixture(scope='session')
def pygame_loop(init_pygame):
    screen = init_pygame
    screen.fill((0, 0, 0))
    clock = pygame.time.Clock()

    def loop(event_handler):
        while True:
            events = pygame.event.get()

            for event in events:
                if event.type == pygame.QUIT or\
                        (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    screen.fill((0, 0, 0))
                    pygame.display.update()
                    return

            pygame.display.update(event_handler(screen, events))
            clock.tick(5)

            if os.environ.get('SDL_VIDEODRIVER') == "dummy":
                # Automatic tests without video device available
                break

    return loop


@pytest.fixture(scope='session')
def scene_builder():

    def create(name):
        background_sprite = sprites.ImageSprite(None, (0, 0, 0), size=(400, 400), layer=0)
        background_sprite.set_crop()
        statusbar_sprite = sprites.StatusBarSprite(None)
        statusbar_sprite.set_rect(0, 250, 30, 160)

        scene = get_scene('pygame', name)
        scene.add_sprite(background_sprite)
        scene.add_sprite(statusbar_sprite)
        scene.set_outlines(True)
        scene.set_text_color((255, 255, 255))
        scene.set_arrows(scene.ARROW_BOTTOM, 0)
        scene.resize((400, 400))
        return scene

    return create


# --- Camera drivers ----------------------------------------------------------


@pytest.fixture(scope='session')
def proxy_cv(init_pygame, init_tasks):
    if os.environ.get('CAMERA_CVDRIVER') == "dummy":
        pytest.importorskip('cv2', reason="OpenCV is not installed")
        return camera_drivers.CvCameraProxyMock(os.path.join(CAPTURES_DIR, 'portrait', 'capture0.png'))
    proxy = get_cv_camera_proxy()
    if proxy is None:
        pytest.skip("No OpenCV camera connected (set CAMERA_CVDRIVER=dummy to use a fake one)")
    return proxy


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
def proxy_gp(init_pygame, init_tasks, captures_portrait):
    if os.environ.get('CAMERA_GPDRIVER') == "dummy":
        from pibooth.camera import gphoto
        gphoto.gp = camera_drivers.GpCameraProxyMock([])
        return camera_drivers.GpCameraProxyMock(captures_portrait)
    proxy = get_gp_camera_proxy()
    if proxy is None:
        pytest.skip("No gPhoto2 camera connected (set CAMERA_GPDRIVER=dummy to use a fake one)")
    return proxy


@pytest.fixture(scope='session')
def camera_gp(proxy_gp):
    cam = GpCamera(proxy_gp)
    cam.initialize(ISO, RESOLUTION, delete_internal_memory=True)
    yield cam
    cam.quit()
