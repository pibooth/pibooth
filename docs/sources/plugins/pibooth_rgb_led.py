"""Plugin to manage the RGB lights via GPIO."""

import pibooth
from gpiozero import RGBLED
from colorzero import Color

__version__ = "1.1.0"

@pibooth.hookimpl
def pibooth_startup(app):
    # GPIOZERO is configured as BCM, use string with "BOARD(pin)" to
    # convert on BOARD
    app.rgbled = RGBLED("BOARD36", "BOARD38", "BOARD40")

@pibooth.hookimpl
def state_wait_enter(app):
    app.rgbled.color = Color('green')

@pibooth.hookimpl
def state_choose_enter(app):
    app.rgbled.blink()

@pibooth.hookimpl
def state_preview_enter(app):
    app.rgbled.color = Color('white')
    app.rgbled.blink()

@pibooth.hookimpl
def state_capture_exit(app):
    app.rgbled.color = Color('red')
