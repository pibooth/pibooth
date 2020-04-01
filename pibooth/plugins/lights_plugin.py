# -*- coding: utf-8 -*-

import time
import pibooth


class LightsPlugin(object):

    """Plugin to manage the lights via GPIO.
    """

    @pibooth.hookimpl
    def pibooth_startup(self, app):
        app.led_startup.switch_on()

    @pibooth.hookimpl
    def pibooth_cleanup(self, app):
        app.led_startup.quit()
        app.led_preview.quit()
        app.led_capture.quit()
        app.led_print.quit()

    @pibooth.hookimpl
    def state_wait_enter(self, app):
        app.led_capture.blink()
        if app.previous_picture_file and app.printer.is_installed() and not app.printer_unavailable:
            app.led_print.blink()

    @pibooth.hookimpl
    def state_wait_do(self, cfg, app, events):
        if app.find_print_event(events) and app.previous_picture_file and app.printer.is_installed():
            app.led_print.switch_on()
            time.sleep(1)  # Just to let the LED switched on

            if app.nbr_duplicates >= cfg.getint('PRINTER', 'max_duplicates') or app.printer_unavailable:
                app.led_print.switch_off()
            else:
                app.led_print.blink()

    @pibooth.hookimpl
    def state_wait_exit(self, app):
        app.led_capture.switch_off()
        app.led_print.switch_off()

    @pibooth.hookimpl
    def state_choose_enter(self, app):
        app.led_capture.blink()
        app.led_print.blink()

    @pibooth.hookimpl
    def state_choose_exit(self, app):
        if app.capture_nbr == app.capture_choices[0]:
            app.led_capture.switch_on()
            app.led_print.switch_off()
        elif app.capture_nbr == app.capture_choices[1]:
            app.led_print.switch_on()
            app.led_capture.switch_off()

    @pibooth.hookimpl
    def state_chosen_exit(self, app):
        app.led_capture.switch_off()
        app.led_print.switch_off()

    @pibooth.hookimpl
    def state_preview_enter(self, app):
        app.led_preview.switch_on()

    @pibooth.hookimpl
    def state_capture_exit(self, app):
        app.led_preview.switch_off()

    @pibooth.hookimpl
    def state_print_enter(self, app):
        app.led_print.blink()

    @pibooth.hookimpl
    def state_print_do(self, app, events):
        if app.find_print_event(events) and app.previous_picture_file:
            app.led_print.switch_on()

    @pibooth.hookimpl
    def state_print_exit(self, app):
        if app.previous_picture_file:
            app.led_print.blink()
