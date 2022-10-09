# -*- coding: utf-8 -*-

"""NoGuiWindow class to emulate a dummy window.
"""

from functools import partial
import pygame

from pibooth import evtfilters
from pibooth.utils import LOGGER
from pibooth.view.base import BaseWindow, BaseScene


class NoGuiScene(BaseScene):

    def set_outlines(self, enable=True): pass

    def set_image(self, image=None): pass

    def set_background(self, color_or_path, size): pass

    def set_text_color(self, color): pass

    def set_arrows(self, location, offset): pass

    def set_print_number(self, current_nbr=None, failure=False):
        self.nop('set_print_number', current_nbr, failure)

    def nop(self, attr, *args, **kwargs):
        LOGGER.info(" @@@@@ Scene(%s) @@@@@ : %s(%s)", self.name, attr,
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
        super(NoGuiWindow, self).__init__(size, background, text_color, arrow_location, arrow_offset, debug)
        LOGGER.info(" @@@@@ NoGuiWindow @@@@@ : %s", title)

        pygame.init()  # Necessary to enable pygame event loop

    def _create_scene(self, name):
        return NoGuiScene(name)

    def eventloop(self, app_update):
        """Main GUI events loop (blocking).
        """
        fps = 25
        clock = pygame.time.Clock()

        while True:
            events = list(pygame.event.get())

            # Convert Pygame events to pibooth events (plugins are based on them)
            for event in events:
                if event.type == pygame.QUIT:
                    return

                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    LOGGER.debug("[ESC] pressed. No menu configured -> exit")
                    return

                if event.type == pygame.KEYDOWN and event.key == pygame.K_c:
                    evtfilters.post_capture_button_event()

                if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                    evtfilters.post_print_button_event()

            # Update application and plugins according to user events
            app_update(events)

            # Ensure the program will never run at more than <fps> frames per second
            clock.tick(fps)
