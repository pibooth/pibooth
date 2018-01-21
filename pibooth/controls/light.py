# -*- coding: utf-8 -*-

import threading
from RPi import GPIO


class PtbLed(object):

    """LED management
    """

    def __init__(self, pin):
        self.pin = pin
        GPIO.setup(pin, GPIO.OUT)
        self._stop = threading.Event()
        self._blinking_thread = None

    def _blink(self, ton=0.3, toff=0.3):
        while not self._stop.is_set():
            GPIO.output(self.pin, GPIO.HIGH)
            if self._stop.wait(ton):
                break  # Stop requested
            GPIO.output(self.pin, GPIO.LOW)
            if self._stop.wait(toff):
                break  # Stop requested

    def _stop_blink(self):
        if self._blinking_thread:
            self._stop.set()
            self._blinking_thread.join()
            self._blinking_thread = None
            self._stop.clear()

    def switch_on(self):
        """Switch on the LED.
        """
        self._stop_blink()
        GPIO.output(self.pin, GPIO.HIGH)

    def switch_off(self):
        """Switch off the LED.
        """
        self._stop_blink()
        GPIO.output(self.pin, GPIO.LOW)

    def blink(self, duration=None):
        """Blink the LED. This method is blocking if a duration (in seconds)
        is given.
        """
        if not self._blinking_thread:
            self._blinking_thread = threading.Thread(target=self._blink)
            self._blinking_thread.daemon = True
            self._blinking_thread.start()

        if duration:
            self._blinking_thread.join(duration)
            self._stop_blink()
