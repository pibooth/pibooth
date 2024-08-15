# -*- coding: utf-8 -*-

import time
import math
import pibooth
from pibooth import evts
from pibooth import camera
from pibooth.language import get_translated_text
from pibooth.utils import LOGGER, PollingTimer


class CameraPlugin:

    """Plugin to manage the camera captures.
    """

    __name__ = 'pibooth-core:camera'

    def __init__(self, plugin_manager):
        self._pm = plugin_manager
        self.timer = PollingTimer()
        self.capture_count = 0

    @pibooth.hookimpl(hookwrapper=True)
    def pibooth_setup_camera(self, cfg):
        outcome = yield  # all corresponding hookimpls are invoked here
        cam = outcome.get_result()

        if not cam:
            LOGGER.debug("Use pibooth camera management system")
            cam = camera.find_camera()

        cam.initialize(cfg.gettuple('CAMERA', 'iso', (int, str), 2),
        cam.initialize(cfg.gettuple('CAMERA', 'iso', (int, str), 2),
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
    def state_preview_enter(self, cfg, app, win):
        LOGGER.info("Show preview before next capture")
        border = 100
        app.camera.preview(win.get_rect(absolute=True).inflate(-border, -border))
        self.timer.start(cfg.getint('WINDOW', 'preview_delay'))

    @pibooth.hookimpl
    def state_preview_do(self, cfg, app):
        if cfg.getboolean('WINDOW', 'preview_countdown'):
            if self.timer.remaining() > 0.5:
                app.camera.set_overlay(math.ceil(self.timer.remaining()))
        if self.timer.remaining() <= 0.5:
            app.camera.set_overlay(get_translated_text('smile'))

    @pibooth.hookimpl
    def state_preview_validate(self):
        if self.timer.is_timeout():
            return 'capture'

    @pibooth.hookimpl
    def state_capture_enter(self, cfg, app):
        effects = cfg.gettyped('PICTURE', 'captures_effects')
        if not app.capture_date:
            app.capture_date = time.strftime("%Y-%m-%d-%H-%M-%S")

        if not isinstance(effects, (list, tuple)):
            # Same effect for all captures
            effect = effects
        elif len(effects) >= app.capture_nbr:
            # Take the effect corresponding to the current capture
            effect = effects[self.capture_count]
        else:
            # Not possible
            raise ValueError(f"Not enough effects defined for {app.capture_nbr} captures {effects}")

        LOGGER.info("Take a capture")
        app.camera.capture(effect)

    @pibooth.hookimpl
    def state_capture_do(self, events):
        event = evts.find_event(events, evts.EVT_PIBOOTH_CAM_CAPTURE)
        if event:
            self.capture_count += 1

    @pibooth.hookimpl
    def state_processing_enter(self, app):
        self.capture_count = 0
        LOGGER.info("Stopping preview")
        app.camera.stop_preview()
