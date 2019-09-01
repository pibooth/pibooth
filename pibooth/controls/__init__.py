# -*- coding: utf-8 -*-

try:
    from RPi import GPIO
except ImportError:
    # GPIO library only existes on Raspberry Pi
    from pibooth.controls.gpio import GpioMock
    GPIO = GpioMock()
