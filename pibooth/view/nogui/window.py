# -*- coding: utf-8 -*-

"""NoGuiWindow class to emulate a dummy window.
"""

from functools import partial
import pygame

from pibooth import evts
from pibooth.utils import LOGGER
from pibooth.view.base import BaseWindow, BaseScene


class NoGuiScene(BaseScene):

    count_flash = 3
    selection = None
    choices = []

    def resize(self, size): pass  # Avoid "NotImplemented" error

    def set_outlines(self, enable=True): pass  # Avoid "NotImplemented" error

    def set_image(self, image=None, stream=False): pass  # Avoid "NotImplemented" error

    def set_text_color(self, color): pass  # Avoid "NotImplemented" error

    def set_arrows(self, location, offset): pass  # Avoid "NotImplemented" error

    def set_choices(self, choices):
        self.choices = choices

    def next(self):
        if not self.selection:
            self.selection = self.choices[1]
        else:
            self.selection = self.choices[(self.choices.index(self.selection)+1) % len(self.choices)]

    def get_selection(self):
        if not self.selection:
            self.selection = self.choices[0]
        return self.selection

    def nop(self, attr, *args, **kwargs):
        LOGGER.info("Scene(%s).%s(%s)", self.name, attr,
                    ','.join([str(v) for v in args] + ["{k}={v}" for k, v in kwargs.items()]))

    def __getattr__(self, attr):
        return partial(self.nop, attr)


class NoGuiWindow(BaseWindow):

    """Class to print view changes in terminal (useful for tests).
    """

    def __init__(self, title,
                 size=(800, 480),
                 background=(0, 0, 0),
                 text_color=(255, 255, 255),
                 arrow_location=BaseScene.ARROW_BOTTOM,
                 arrow_offset=0,
                 debug=False):
        super().__init__(size, background, text_color, arrow_location, arrow_offset, debug)
        LOGGER.info("@@@@@ %s @@@@@ : %s", self.__class__.__name__, title)

        pygame.init()  # Necessary to enable pygame event loop

    def eventloop(self, app_update):
        """Main GUI events loop (blocking).
        """
        fps = 25
        clock = pygame.time.Clock()

        while True:
            events = list(pygame.event.get())

            # 0. Update application and plugins according to user events,
            #    it may update view elements internal variables
            app_update(events)

            # 1. Convert Pygame events to pibooth events (plugins are based on them)
            for event in events:
                if event.type == pygame.QUIT:
                    return

                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE\
                        or event.type == evts.EVT_BUTTON_SETTINGS:
                    LOGGER.debug("[ESC] pressed. No menu configured -> exit")
                    return

                if (event.type == pygame.KEYDOWN and event.key == pygame.K_c)\
                        or event.type == evts.EVT_BUTTON_CAPTURE:
                    LOGGER.debug("Event triggered: KEY C -> generate EVT_BUTTON_CAPTURE")
                    evts.post(evts.EVT_PIBOOTH_CAPTURE)

                if event.type == pygame.KEYDOWN and event.key == pygame.K_p\
                        or event.type == evts.EVT_BUTTON_PRINT:
                    LOGGER.debug("Event triggered: KEY P -> generate EVT_BUTTON_PRINT")
                    evts.post(evts.EVT_PIBOOTH_PRINT)

            # 2. Ensure the program will never run at more than <fps> frames per second
            clock.tick(fps)
