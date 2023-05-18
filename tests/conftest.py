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
from pibooth.camera import get_rpi_camera_proxy, get_libcamera_camera_proxy, get_gp_camera_proxy, get_cv_camera_proxy
from pibooth.camera import RpiCamera, LibCamera, GpCamera, CvCamera, HybridRpiCamera, HybridLibCamera, HybridCvCamera

# Modules for tests purpose
import pytest
from mocks import camera_drivers


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
    return Counters(str(tmpdir.join('data.pickle')), nbr_printed=0)


@pytest.fixture(scope='session')
def printer():
    os.system('lpadmin -p nowhere -E -v file:/dev/null')
    return Printer('nowhere')


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
def proxy_rpi(init_pygame, init_tasks, captures_portrait):
    if os.environ.get('CAMERA_RPIDRIVER') == "dummy":
        RpiCamera.IMAGE_EFFECTS = ['none']
        return camera_drivers.RpiCameraProxyMock(captures_portrait)
    return get_rpi_camera_proxy()


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
def proxy_libcamera(init_pygame, init_tasks, captures_portrait):
    if os.environ.get('CAMERA_LIBCAMDRIVER') == "dummy":
        from pibooth.camera import libcamera
        libcamera.Transform = camera_drivers.LibcameraCameraProxyMock.Transform  # Monkey patch
        return camera_drivers.LibcameraCameraProxyMock(captures_portrait)
    return get_libcamera_camera_proxy()


@pytest.fixture(scope='session')
def camera_libcamera(proxy_libcamera):
    cam = LibCamera(proxy_libcamera)
    cam.initialize(ISO, RESOLUTION, delete_internal_memory=True)
    yield cam
    cam.quit()


@pytest.fixture(scope='session')
def camera_libcamera_gp(proxy_libcamera, proxy_gp):
    cam = HybridLibCamera(proxy_libcamera, proxy_gp)
    cam.initialize(ISO, RESOLUTION, delete_internal_memory=True)
    yield cam
    cam.quit()


@pytest.fixture(scope='session')
def proxy_cv(init_pygame, init_tasks):
    if os.environ.get('CAMERA_CVDRIVER') == "dummy":
        import cv2
        return cv2.VideoCapture(os.path.join(CAPTURES_DIR, 'portrait', 'capture0.png'))
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
def proxy_gp(init_pygame, init_tasks, captures_portrait):
    if os.environ.get('CAMERA_GPDRIVER') == "dummy":
        from pibooth.camera import gphoto
        gphoto.gp = camera_drivers.GpCameraProxyMock(captures_portrait)  # Monkey patch
        return gphoto.gp
    return get_gp_camera_proxy()


@pytest.fixture(scope='session')
def camera_gp(proxy_gp):
    cam = GpCamera(proxy_gp)
    cam.initialize(ISO, RESOLUTION, delete_internal_memory=True)
    yield cam
    cam.quit()
