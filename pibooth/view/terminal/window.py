# -*- coding: utf-8 -*-

import pygame
from functools import partial

from pibooth.utils import LOGGER
from pibooth.view.base import BaseWindow, BaseScene


class TerminalScene(BaseScene):

    def nop(self, attr, *args, **kwargs):
        LOGGER.info(" @@@@@ Scene(%s) @@@@@ : %s(%s)", self.name, attr,
                    ','.join([str(v) for v in args] + ["{k}={v}" for k, v in kwargs.items()]))

    def __getattr__(self, attr):
        return partial(self.nop, attr)


class TerminalWindow(BaseWindow):

    """Class to print view changes in terminal (useful for tests).
    """

    def __init__(self, title,
                 size=(800, 480),
                 bg_color=(0, 0, 0),
                 text_color=(255, 255, 255),
                 arrow_location=BaseWindow.ARROW_BOTTOM,
                 arrow_offset=0,
                 debug=False):
        super(TerminalWindow, self).__init__(size, bg_color, text_color, arrow_location, arrow_offset, debug)
        LOGGER.info(" @@@@@ TerminalWindow @@@@@ : %s", title)

        pygame.init()  # Necessary to enable pygame event loop

    def _create_scene(self, name):
        return TerminalScene(name)
