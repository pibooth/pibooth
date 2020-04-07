# -*- coding: utf-8 -*-

import time
import pibooth
from pibooth.utils import LOGGER
from gpiozero import Device, LEDBoard
try:
    from RPi import GPIO
    LOGGER.info("Start on Raspberry pi")
except ImportError:
    # GPIO library only existes on Raspberry Pi
    # Set the default pin factory to a mock factory
    from gpiozero.pins.mock import MockFactory
    Device.pin_factory = MockFactory()
    LOGGER.info("Programme not start on Raspberry pi use MockFactory() mode")


class LightsPlugin(object):

    """Plugin to manage the lights via GPIO.
    """
    def __init__(self):
        self.blink_time = 0.3
        self.load = False

    def start(self, cfg):

        if not self.load:
            self.leds = LEDBoard(
                            led_capture="BOARD" + cfg.get('CONTROLS', 'picture_led_pin'),
                            led_print="BOARD" + cfg.get('CONTROLS', 'print_led_pin'),
                            led_preview="BOARD" + cfg.get('CONTROLS', 'preview_led_pin'),
                            led_start="BOARD" + cfg.get('CONTROLS', 'startup_led_pin'),
                            # pwm=True
                    )
            self.leds.led_start.on()
            self.load = True

    @pibooth.hookimpl
    def state_wait_enter(self, cfg, app):
        self.start(cfg)
        self.leds.led_capture.blink(on_time=self.blink_time, off_time=self.blink_time, n=None, background=True)
        if app.previous_picture_file and app.printer.is_installed() and not app.printer_unavailable:
            self.leds.led_print.blink(on_time=self.blink_time, off_time=self.blink_time, n=None, background=True)

    @pibooth.hookimpl
    def state_wait_do(self, cfg, app, events):
        if app.find_print_event(events) and app.previous_picture_file and app.printer.is_installed():
            self.leds.led_print.on()
            time.sleep(1)  # Just to let the LED switched on

            if app.nbr_duplicates >= cfg.getint('PRINTER', 'max_duplicates') or app.printer_unavailable:
                self.leds.led_print.off()
            else:
                self.leds.led_print.blink(on_time=self.blink_time, off_time=self.blink_time, n=None, background=True)

    @pibooth.hookimpl
    def state_wait_exit(self):
        self.leds.led_capture.off()
        self.leds.led_print.off()

    @pibooth.hookimpl
    def state_choose_enter(self):
        self.leds.led_capture.blink(on_time=self.blink_time, off_time=self.blink_time, n=None, background=True)
        self.leds.led_print.blink(on_time=self.blink_time, off_time=self.blink_time, n=None, background=True)

    @pibooth.hookimpl
    def state_choose_exit(self, app):
        if app.capture_nbr == app.capture_choices[0]:
            self.leds.led_capture.on()
            self.leds.led_print.off()
        elif app.capture_nbr == app.capture_choices[1]:
            self.leds.led_print.on()
            self.leds.led_capture.off()

    @pibooth.hookimpl
    def state_chosen_exit(self):
        self.leds.led_capture.off()
        self.leds.led_print.off()

    @pibooth.hookimpl
    def state_preview_enter(self):
        self.leds.led_preview.on()

    @pibooth.hookimpl
    def state_capture_exit(self):
        self.leds.led_preview.off()

    @pibooth.hookimpl
    def state_print_enter(self):
        self.leds.led_print.blink(on_time=self.blink_time, off_time=self.blink_time, n=None, background=True)

    @pibooth.hookimpl
    def state_print_do(self, app, events):
        if app.find_print_event(events) and app.previous_picture_file:
            self.leds.led_print.on()

    @pibooth.hookimpl
    def state_print_exit(self, app):
        if app.previous_picture_file:
            self.leds.led_print.blink(on_time=self.blink_time, off_time=self.blink_time, n=None, background=True)
