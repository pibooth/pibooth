# -*- coding: utf-8 -*-

import time
import math
import pygame
import pibooth
from pibooth import camera
from pibooth.language import get_translated_text
from pibooth.utils import LOGGER, PoolingTimer


class CameraPlugin(object):

    """Plugin to manage the camera captures.
    """

    def __init__(self, plugin_manager):
        self._pm = plugin_manager
        self.count = 0
        # Seconds to display the preview
        self.preview_timer = PoolingTimer(3)

    @pibooth.hookimpl(hookwrapper=True)
    def pibooth_setup_camera(self, cfg):
        outcome = yield  # all corresponding hookimpls are invoked here
        cam = outcome.get_result()

        if not cam:
            LOGGER.debug("Fallback to pibooth default camera management system")
            cam = camera.find_camera()

        cam.initialize(cfg.gettuple('CAMERA', 'iso', int, 2),
                       cfg.gettyped('CAMERA', 'resolution'),
                       cfg.gettuple('CAMERA', 'rotation', int, 2),
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
        if len(app.capture_choices) > 1:
            app.capture_nbr = None
        else:
            app.capture_nbr = app.capture_choices[0]

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
        if not app.capture_date:
            app.capture_date = time.strftime("%Y-%m-%d-%H-%M-%S")

        border = 100
        app.camera.preview(win.get_rect(absolute=True).inflate(-border, -border))
        self.preview_timer.timeout = cfg.getint('WINDOW', 'preview_delay')
        self.preview_timer.start()

    @pibooth.hookimpl
    def state_preview_do(self, cfg, app, win, events):
        if cfg.getboolean('WINDOW', 'preview_countdown'):
            if self.preview_timer.remaining() > 0.5:
                app.camera.set_overlay(math.ceil(self.preview_timer.remaining()))
            else:
                app.camera.set_overlay(get_translated_text('smile'))
        for event in events:
            if event.type == camera.EVT_CAMERA_CAPTURE:
                if event.error:
                    LOGGER.error("Camera preview failure", exc_info=event.error)
                    raise IOError("Can not get preview capture!")
                win.show_image(event.image)

    @pibooth.hookimpl
    def state_preview_validate(self):
        if self.preview_timer.is_timeout():
            return 'capture'

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

        LOGGER.info("Take a capture")
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
