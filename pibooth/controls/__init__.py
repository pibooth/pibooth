# -*- coding: utf-8 -*-

from pibooth.utils import LOGGER
from gpiozero import Device, LEDBoard
try:
    from RPi import GPIO
    LOGGER.debug("Start on Raspberry pi")
except ImportError:
    # GPIO library only existes on Raspberry Pi
    # Set the default pin factory to a mock factory
    from gpiozero.pins.mock import MockFactory
    Device.pin_factory = MockFactory()
    LOGGER.debug("Programme not start on Raspberry pi use MockFactory() mode")