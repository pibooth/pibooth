# -*- coding: utf-8 -*-

import time
import pibooth


class LightsPlugin(object):
    """Plugin to manage the lights via GPIO.
    """

    name = 'pibooth-core:lights'

    def __init__(self, plugin_manager):
        self._pm = plugin_manager
        self.blink_time = 0.3


    @pibooth.hookimpl
    def state_wait_enter(self, app):
        if app.previous_picture_file and app.printer.is_ready()\
                and app.count.remaining_duplicates > 0:
            app.leds.blink(on_time=self.blink_time, off_time=self.blink_time)
            try:
                app.mcp2221_picture_led.value = True
                app.mcp2221_print_led.value = True
            except AttributeError:
                pass

        else:
            app.leds.capture.blink(on_time=self.blink_time, off_time=self.blink_time)
            app.leds.printer.off()
            try:
                app.mcp2221_picture_led.value = True
                app.mcp2221_print_led.value = False
            except AttributeError:
                pass

    @pibooth.hookimpl
    def state_wait_do(self, app, events):
        if app.find_print_event(events) and app.previous_picture_file and app.printer.is_ready():
            if app.count.remaining_duplicates <= 0:
                app.leds.printer.off()
                try:
                    app.mcp2221_print_led.value = False
                except AttributeError:
                    pass
            else:
                app.leds.printer.on()
                try:
                    app.mcp2221_print_led.value = True
                except AttributeError:
                    pass
                time.sleep(1)  # Just to let the LED switched on
                app.leds.blink(on_time=self.blink_time, off_time=self.blink_time)

        if not app.previous_picture_file and app.leds.printer._controller:  # _controller == blinking
            app.leds.printer.off()

    @pibooth.hookimpl
    def state_wait_exit(self, app):
        app.leds.off()
        try:
            app.mcp2221_picture_led.value = False
            app.mcp2221_print_led.value = False
        except AttributeError:
            pass

    @pibooth.hookimpl
    def state_choose_enter(self, app):
        app.leds.blink(on_time=self.blink_time, off_time=self.blink_time)
        try:
            app.mcp2221_picture_led.value = True
            app.mcp2221_print_led.value = True
        except AttributeError:
            pass

    @pibooth.hookimpl
    def state_choose_exit(self, app):
        if app.capture_nbr == app.capture_choices[0]:
            app.leds.capture.on()
            app.leds.printer.off()
            try:
                app.mcp2221_picture_led.value = True
                app.mcp2221_print_led.value = False
            except AttributeError:
                pass
        elif app.capture_nbr == app.capture_choices[1]:
            app.leds.printer.on()
            app.leds.capture.off()
            try:
                app.mcp2221_picture_led.value = False
                app.mcp2221_print_led.value = True
            except AttributeError:
                pass

    @pibooth.hookimpl
    def state_chosen_exit(self, app):
        app.leds.off()
        try:
            app.mcp2221_picture_led.value = False
            app.mcp2221_print_led.value = False
        except AttributeError:
            pass

    @pibooth.hookimpl
    def state_print_enter(self, app):
        app.leds.blink(on_time=self.blink_time, off_time=self.blink_time)
        try:
            app.mcp2221_picture_led.value = True
            app.mcp2221_print_led.value = True
        except AttributeError:
            pass

    @pibooth.hookimpl
    def state_print_do(self, app, events):
        if app.find_print_event(events):
            app.leds.printer.on()
            app.leds.capture.off()
            try:
                app.mcp2221_picture_led.value = False
                app.mcp2221_print_led.value = True
            except AttributeError:
                pass

    @pibooth.hookimpl
    def state_finish_enter(self, app):
        app.leds.off()
        try:
            app.mcp2221_picture_led.value = False
            app.mcp2221_print_led.value = False
        except AttributeError:
            pass
