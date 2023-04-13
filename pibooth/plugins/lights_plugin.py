# -*- coding: utf-8 -*-

import pibooth
from pibooth import evts


class LightsPlugin:
    """Plugin to manage the lights via GPIO.
    """

    __name__ = 'pibooth-core:lights'

    def __init__(self, plugin_manager):
        self._pm = plugin_manager
        self.blink_time = 0.3

    @pibooth.hookimpl
    def state_wait_enter(self, app):
        if app.previous_picture_file and app.printer.is_ready()\
                and app.count.remaining_duplicates > 0:
            app.leds.blink(on_time=self.blink_time, off_time=self.blink_time)
        else:
            app.leds.capture.blink(on_time=self.blink_time, off_time=self.blink_time)
            app.leds.printer.off()

    @pibooth.hookimpl
    def state_wait_do(self, app, events):
        if evts.find_event(events, evts.EVT_PIBOOTH_PRINT) and app.previous_picture_file and app.printer.is_ready():
            if app.count.remaining_duplicates <= 0:
                app.leds.printer.off()

        if not app.previous_picture_file and app.leds.printer._controller:  # _controller == blinking
            app.leds.printer.off()

    @pibooth.hookimpl
    def state_wait_exit(self, app):
        app.leds.off()

    @pibooth.hookimpl
    def state_choose_enter(self, app):
        app.leds.blink(on_time=self.blink_time, off_time=self.blink_time)

    @pibooth.hookimpl
    def state_choose_exit(self, app):
        app.leds.capture.off()
        app.leds.printer.off()

    @pibooth.hookimpl
    def state_print_enter(self, app):
        app.leds.blink(on_time=self.blink_time, off_time=self.blink_time)

    @pibooth.hookimpl
    def state_print_do(self, app, events):
        if evts.find_event(events, evts.EVT_PIBOOTH_PRINT):
            app.leds.printer.on()
            app.leds.capture.off()

    @pibooth.hookimpl
    def state_finish_enter(self, app):
        app.leds.off()
