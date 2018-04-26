# -*- coding: utf-8 -*-

"""
Mocks for tests on other HW than Raspberry Pi.
"""


class GPIO(object):

    BOARD = 'board'
    IN = 'in'
    OUT = 'out'
    PUD_UP = 'pud_up'
    FALLING = 'falling'
    HIGH = 'high'
    LOW = 'low'

    @classmethod
    def setmode(cls, mode):
        print("Mock: set GPIO mode {}".format(mode))

    @classmethod
    def setup(cls, pin, direction, **kwargs):
        print("Mock: setup GPIO pin {} to {}".format(pin, direction))

    @classmethod
    def output(cls, pin, status):
        print("Mock: output GPIO pin {} to {}".format(pin, status))

    @classmethod
    def add_event_detect(cls, pin, status, **kwargs):
        print("Mock: detect GPIO pin {} when {}".format(pin, status))

    @classmethod
    def cleanup(cls):
        print("Mock: quit GPIO")
