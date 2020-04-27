# -*- coding: utf-8 -*-

import time
import pibooth


class LightsPlugin(object):
    """Plugin to manage the lights via GPIO.
    """

    def __init__(self, plugin_manager):
        self._pm = plugin_manager
        self.blink_time = 0.3

    @pibooth.hookimpl
    def pibooth_startup(self, app):
        app.leds.start.on()

    @pibooth.hookimpl
    def state_wait_enter(self, app):
        app.button_synced_leds.capture.blink(on_time=self.blink_time, off_time=self.blink_time)
        if app.previous_picture_file and app.printer.is_installed() and not app.printer_unavailable:
            app.button_synced_leds.blink(on_time=self.blink_time, off_time=self.blink_time)
        elif not app.previous_picture_file:
            app.button_synced_leds.printer.off()

    @pibooth.hookimpl
    def state_wait_do(self, cfg, app, events):
        if app.find_print_event(events) and app.previous_picture_file and app.printer.is_installed():
            app.button_synced_leds.printer.on()
            time.sleep(1)  # Just to let the LED switched on

            if app.nbr_duplicates >= cfg.getint('PRINTER', 'max_duplicates') or app.printer_unavailable:
                app.button_synced_leds.printer.off()
            else:
                app.button_synced_leds.printer.blink(on_time=self.blink_time, off_time=self.blink_time)

    @pibooth.hookimpl
    def state_wait_exit(self, app):
        app.button_synced_leds.off()

    @pibooth.hookimpl
    def state_choose_enter(self, app):
        app.button_synced_leds.blink(on_time=self.blink_time, off_time=self.blink_time)

    @pibooth.hookimpl
    def state_choose_exit(self, app):
        if app.capture_nbr == app.capture_choices[0]:
            app.button_synced_leds.capture.on()
            app.button_synced_leds.printer.off()
        elif app.capture_nbr == app.capture_choices[1]:
            app.button_synced_leds.printer.on()
            app.button_synced_leds.capture.off()

    @pibooth.hookimpl
    def state_chosen_exit(self, app):
        app.button_synced_leds.off()

    @pibooth.hookimpl
    def state_preview_enter(self, app):
        app.leds.preview.on()

    @pibooth.hookimpl
    def state_capture_exit(self, app):
        app.leds.preview.off()

    @pibooth.hookimpl
    def state_print_do(self, app, events):
        app.button_synced_leds.blink(on_time=self.blink_time, off_time=self.blink_time)
        if app.find_print_event(events) and app.previous_picture_file:
            app.button_synced_leds.printer.on()
            app.button_synced_leds.capture.off()