# -*- coding: utf-8 -*-

"""
Mocks for tests on other HW than Raspberry Pi.
Pin can be triggered using::

    $ kill -<GPIO pin number> <pibooth PID>
"""

import os
import time
import signal
from functools import partial
from pibooth.utils import LOGGER


class GpioMock(object):

    BOARD = 'board'
    IN = 'in'
    OUT = 'out'
    PUD_UP = 'pud_up'
    FALLING = 'falling'
    HIGH = 'high'
    LOW = 'low'

    def __init__(self):
        self._last_signal_time = {}

    def _on_signal(self, pin, frame, callback, bouncetime):
        last = self._last_signal_time.setdefault(pin, 0)
        if abs(time.time() - last) * 1000 >= bouncetime:
            LOGGER.debug('GPIO Mock: pin %s triggered', pin)
            self._last_signal_time[pin] = time.time()
            callback(pin)

    def setmode(self, mode):
        LOGGER.debug("GPIO Mock: set mode %s", mode)

    def setup(self, pin, direction, **kwargs):
        LOGGER.debug("GPIO Mock: setup pin %s to %s", pin, direction)

    def output(self, pin, status):
        pass

    def add_event_detect(self, pin, status, **kwargs):
        LOGGER.debug("GPIO Mock: add detection on pin %s when %s", pin, status)
        callback = kwargs.get('callback')
        bouncetime = kwargs.get('bouncetime', 0)
        if callback:
            LOGGER.info("GPIO Mock: trigger pin %s by typing 'kill -%s %s'", pin, pin, os.getpid())
            signal.signal(pin, partial(self._on_signal, callback=callback, bouncetime=bouncetime))

    def cleanup(self):
        LOGGER.debug("GPIO Mock: quit")
