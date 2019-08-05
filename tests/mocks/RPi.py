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


class GpioMock(object):

    BOARD = 'board'
    IN = 'in'
    OUT = 'out'
    PUD_UP = 'pud_up'
    FALLING = 'falling'
    HIGH = 'high'
    LOW = 'low'

    def __init__(self):
        self._last_signal_time = time.time()

    def _on_receive_signal(self, pin, frame, callback, bouncetime):
        if abs(time.time() - self._last_signal_time) * 1000 >= bouncetime:
            print('Mock: GPIO', pin, 'triggered')
            self._last_signal_time = time.time()
            callback(pin)

    def setmode(self, mode):
        print("Mock: set GPIO mode {}".format(mode))

    def setup(self, pin, direction, **kwargs):
        print("Mock: setup GPIO pin {} to {}".format(pin, direction))

    def output(self, pin, status):
        pass

    def add_event_detect(self, pin, status, **kwargs):
        print("Mock: add detection on GPIO pin {} when {}".format(pin, status))
        callback = kwargs.get('callback')
        bouncetime = kwargs.get('bouncetime', 0)
        if callback:
            print("Mock: simulate GPIO", pin, "by typing:")
            print("      $ kill -{} {}".format(pin, os.getpid()))
            signal.signal(pin, partial(self._on_receive_signal, callback=callback,
                                       bouncetime=bouncetime))

    def cleanup(self):
        print("Mock: quit GPIO")


GPIO = GpioMock()
