# -*- coding: utf-8 -*-

import pygame
from RPi import GPIO


BUTTON_DOWN = pygame.USEREVENT + 1


class PtbButton(object):

    """Physical button management
    """

    def __init__(self, pin, bouncetime=0.1):
        self.pin = pin
        # Use internal pull up/down resistors
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        GPIO.add_event_detect(self.pin, GPIO.FALLING,
                              callback=self.on_button_down,
                              bouncetime=int(bouncetime * 1000))

    def __eq__(self, other):
        """Can compare button with its pin.
        """
        if isinstance(other, PtbButton):
            return self is other
        else:
            return self.pin == other

    def on_button_down(self, pin):
        """Post a pygame event when the button is pressed.
        """
        event = pygame.event.Event(BUTTON_DOWN, pin=pin)
        pygame.event.post(event)
