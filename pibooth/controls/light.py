# -*- coding: utf-8 -*-

import threading
from RPi import GPIO


class BlinkingThread(threading.Thread):

    """Thread which manage blinking LEDs synchronously.
    """

    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True

        self._tick = 0.3
        self._stop_event = threading.Event()
        self._leds = []
        self.start()

    def register(self, led):
        """Add a new LED to manage.
        """
        self._leds.append(led)

    def run(self):
        """Cyclic call to the method :py:meth:`PtbLed.toggle_state`
        of the registered LED.
        """
        while not self._stop_event.is_set():
            for led in list(self._leds):  # new list for thread safe
                led.toggle_state()
            if self._stop_event.wait(self._tick):
                break  # Stop requested

    def stop(self):
        """Stop the thread.
        """
        self._stop_event.set()


class PtbLed(object):

    """LED management.
    """

    _blinking_thread = BlinkingThread()

    def __init__(self, pin):
        self.pin = pin
        GPIO.setup(pin, GPIO.OUT)
        self._blink = False
        self._state = GPIO.LOW

        self._blinking_thread.register(self)

    def toggle_state(self):
        """Toogle the LED state.
        """
        if self._blink:
            if self._state == GPIO.LOW:
                GPIO.output(self.pin, GPIO.HIGH)
                self._state = GPIO.HIGH
            else:
                GPIO.output(self.pin, GPIO.LOW)
                self._state = GPIO.LOW

    def switch_on(self):
        """Switch on the LED.
        """
        self._blink = False
        GPIO.output(self.pin, GPIO.HIGH)
        self._state = GPIO.HIGH

    def switch_off(self):
        """Switch off the LED.
        """
        self._blink = False
        GPIO.output(self.pin, GPIO.LOW)
        self._state = GPIO.LOW

    def blink(self):
        """Blink the LED.
        """
        self._blink = True

    def quit(self):
        """Stop the blinking thread.
        """
        self._blinking_thread.stop()
        self._blinking_thread.join()
