# -*- coding: utf-8 -*-

import threading
from RPi import GPIO


class BlinkingThread(threading.Thread):

    """Thread which manage blinking LEDs synchronously.
    """

    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True

        self._leds = []
        self._tick = 0.3
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self.start()

    def register(self, led):
        """Add a new LED to manage.
        """
        with self._lock:
            if led not in self._leds:
                self._leds.append(led)

    def unregister(self, led):
        """Remove the given LED from the blinking management.
        """
        with self._lock:
            if led in self._leds:
                self._leds.remove(led)

    def run(self):
        """Cyclic call to the method :py:meth:`PtbLed.switch_on` and
        :py:meth:`PtbLed.switch_off` of the registered LED.
        """
        sequence = ['switch_on', 'switch_off']
        while not self._stop_event.is_set():
            for func_name in sequence:
                with self._lock:
                    for led in self._leds:
                        getattr(led, func_name)()
                if self._stop_event.wait(self._tick):
                    return  # Stop requested

    def stop(self):
        """Stop the thread.
        """
        self._stop_event.set()
        self.join()


class PtbLed(object):

    """LED management.
    """

    _blinking_thread = BlinkingThread()

    def __init__(self, pin):
        self.pin = pin
        GPIO.setup(pin, GPIO.OUT)

    def switch_on(self):
        """Switch on the LED.
        """
        if threading.current_thread() != self._blinking_thread:
            self._blinking_thread.unregister(self)
        GPIO.output(self.pin, GPIO.HIGH)

    def switch_off(self):
        """Switch off the LED.
        """
        if threading.current_thread() != self._blinking_thread:
            self._blinking_thread.unregister(self)
        GPIO.output(self.pin, GPIO.LOW)

    def blink(self):
        """Blink the LED.
        """
        self._blinking_thread.register(self)

    def quit(self):
        """Switch off and stop the blinking thread.
        """
        self.switch_off()
        self._blinking_thread.stop()
