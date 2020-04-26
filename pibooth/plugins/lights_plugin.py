# -*- coding: utf-8 -*-

import time
import pibooth
from gpiozero import LEDBoard


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
        app.leds_link.capture.blink(on_time=self.blink_time, off_time=self.blink_time)
        if app.previous_picture_file and app.printer.is_installed() and not app.printer_unavailable:
            app.leds_link.blink(on_time=self.blink_time, off_time=self.blink_time)
        elif not app.previous_picture_file:
            app.leds_link.printer.off()

    @pibooth.hookimpl
    def state_wait_do(self, cfg, app, events):
        if app.find_print_event(events) and app.previous_picture_file and app.printer.is_installed():
            app.leds_link.printer.on()
            time.sleep(1)  # Just to let the LED switched on

            if app.nbr_duplicates >= cfg.getint('PRINTER', 'max_duplicates') or app.printer_unavailable:
                app.leds_link.printer.off()
            else:
                app.leds_link.printer.blink(on_time=self.blink_time, off_time=self.blink_time)

    @pibooth.hookimpl
    def state_wait_exit(self, app):
        app.leds_link.off()

    @pibooth.hookimpl
    def state_choose_enter(self, app):
        app.leds_link.blink(on_time=self.blink_time, off_time=self.blink_time)

    @pibooth.hookimpl
    def state_choose_exit(self, app):
        if app.capture_nbr == app.capture_choices[0]:
            app.leds_link.capture.on()
            app.leds_link.printer.off()
        elif app.capture_nbr == app.capture_choices[1]:
            app.leds_link.printer.on()
            app.leds_link.capture.off()

    @pibooth.hookimpl
    def state_chosen_exit(self, app):
        app.leds_link.off()

    @pibooth.hookimpl
    def state_preview_enter(self, app):
        app.leds.preview.on()

    @pibooth.hookimpl
    def state_capture_exit(self, app):
        app.leds.preview.off()

    # @pibooth.hookimpl
    # def state_print_enter(self, app):


    @pibooth.hookimpl
    def state_print_do(self, app, events):
        app.leds_link.blink(on_time=self.blink_time, off_time=self.blink_time)
        # app.leds.printer.blink(on_time=self.blink_time, off_time=self.blink_time)
        if app.find_print_event(events) and app.previous_picture_file:
            app.leds_link.printer.on()
            app.leds_link.capture.off()