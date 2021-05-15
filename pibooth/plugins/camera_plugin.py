# -*- coding: utf-8 -*-

import time
import pygame
import pibooth
from pibooth import camera
from pibooth.utils import LOGGER, timeit


class CameraPlugin(object):

    """Plugin to manage the camera captures.
    """

    def __init__(self, plugin_manager):
        self._pm = plugin_manager
        self.count = 0

    @pibooth.hookimpl(hookwrapper=True)
    def pibooth_setup_camera(self, cfg):
        outcome = yield  # all corresponding hookimpls are invoked here
        cam = outcome.get_result()

        if not cam:
            LOGGER.debug("Fallback to pibooth default camera management system")
            # Initialize the camera depending of the connected one. The priority order
            # is chosen in order to have best rendering during preview and to take
            # captures. The gPhoto2 camera is first (drivers most restrictive) to avoid
            # connection concurence in case of DSLR compatible with OpenCV.
            rpi_cam = camera.find_rpi_camera()
            gp_cam = camera.find_gp_camera()
            cv_cam = camera.find_cv_camera()

            if rpi_cam and gp_cam:
                LOGGER.info("Configuring hybrid camera (Picamera + gPhoto2) ...")
                cam = camera.HybridRpiCamera(rpi_cam, gp_cam)
            elif cv_cam and gp_cam:
                LOGGER.info("Configuring hybrid camera (OpenCV + gPhoto2) ...")
                cam = camera.HybridCvCamera(cv_cam, gp_cam)
            elif gp_cam:
                LOGGER.info("Configuring gPhoto2 camera ...")
                cam = camera.GpCamera(gp_cam)
            elif rpi_cam:
                LOGGER.info("Configuring Picamera camera ...")
                cam = camera.RpiCamera(rpi_cam)
            elif cv_cam:
                LOGGER.info("Configuring OpenCV camera ...")
                cam = camera.CvCamera(cv_cam)
            else:
                raise EnvironmentError("Neither Raspberry Pi nor GPhoto2 nor OpenCV camera detected")

        cam.initialize(cfg.gettuple('CAMERA', 'iso', int, 2),
                       cfg.gettyped('CAMERA', 'resolution'),
                       cfg.getint('CAMERA', 'rotation'),
                       cfg.getboolean('CAMERA', 'flip'),
                       cfg.getboolean('CAMERA', 'delete_internal_memory'))
        outcome.force_result(cam)

    @pibooth.hookimpl
    def pibooth_cleanup(self, app):
        app.camera.quit()

    @pibooth.hookimpl
    def state_failsafe_enter(self, app):
        """Reset variables set in this plugin.
        """
        app.capture_date = None
        app.capture_nbr = None
        app.camera.drop_captures()  # Flush previous captures

    @pibooth.hookimpl
    def state_wait_enter(self, app):
        app.capture_date = None
        app.capture_nbr = None

    @pibooth.hookimpl
    def state_choose_do(self, app, events):
        event = app.find_choice_event(events)
        if event:
            if event.key == pygame.K_LEFT:
                app.capture_nbr = app.capture_choices[0]
            elif event.key == pygame.K_RIGHT:
                app.capture_nbr = app.capture_choices[1]

    @pibooth.hookimpl
    def state_preview_enter(self, cfg, app, win):
        LOGGER.info("Show preview before next capture")
        if not app.capture_nbr:
            app.capture_nbr = app.capture_choices[0]
        if not app.capture_date:
            app.capture_date = time.strftime("%Y-%m-%d-%H-%M-%S")
        app.camera.preview(win)

    @pibooth.hookimpl
    def state_preview_do(self, cfg, app):
        pygame.event.pump()  # Before blocking actions
        if cfg.getboolean('WINDOW', 'preview_countdown'):
            app.camera.preview_countdown(cfg.getint('WINDOW', 'preview_delay'))
        else:
            app.camera.preview_wait(cfg.getint('WINDOW', 'preview_delay'))

    @pibooth.hookimpl
    def state_preview_exit(self, cfg, app):
        if cfg.getboolean('WINDOW', 'preview_stop_on_capture'):
            app.camera.stop_preview()

    @pibooth.hookimpl
    def state_capture_do(self, cfg, app, win):
        effects = cfg.gettyped('PICTURE', 'captures_effects')
        if not isinstance(effects, (list, tuple)):
            # Same effect for all captures
            effect = effects
        elif len(effects) >= app.capture_nbr:
            # Take the effect corresponding to the current capture
            effect = effects[self.count]
        else:
            # Not possible
            raise ValueError("Not enough effects defined for {} captures {}".format(
                app.capture_nbr, effects))

        with timeit("Take a capture"):
            if cfg.getboolean('WINDOW', 'flash'):
                with win.flash(2):  # Manage the window here, have no choice
                    app.camera.capture(effect)
            else:
                app.camera.capture(effect)

        self.count += 1

    @pibooth.hookimpl
    def state_capture_exit(self, cfg, app):
        if not cfg.getboolean('WINDOW', 'preview_stop_on_capture'):
            app.camera.stop_preview()
