# -*- coding: utf-8 -*-


class GPIO(object):

    BOARD = 'board'
    IN = 'in'
    OUT = 'out'
    PUD_UP = 'pud_up'
    FALLING = 'falling'
    HIGH = 'high'
    LOW = 'low'

    @classmethod
    def setmode(cls, *args, **kwargs):
        pass

    @classmethod
    def setup(cls, *args, **kwargs):
        pass

    @classmethod
    def output(cls, *args, **kwargs):
        pass

    @classmethod
    def add_event_detect(cls, *args, **kwargs):
        pass

    @classmethod
    def cleanup(cls):
        pass
