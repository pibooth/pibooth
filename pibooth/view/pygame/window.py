# -*- coding: utf-8 -*-

import os
import pygame

from pibooth import evtfilters
from pibooth.view.base import BaseWindow


class PygameWindow(BaseWindow):

    """Class to create window using Pygame.
    """

    def __init__(self, title,
                 size=(800, 480),
                 background=(0, 0, 0),
                 text_color=(255, 255, 255),
                 arrow_location=BaseWindow.ARROW_BOTTOM,
                 arrow_offset=0,
                 debug=False):
        super(PygameWindow, self).__init__(size, background, text_color, arrow_location, arrow_offset, debug)

        # Prepare the pygame module for use
        if 'SDL_VIDEO_WINDOW_POS' not in os.environ:
            os.environ['SDL_VIDEO_CENTERED'] = '1'
        pygame.init()

        # Save the desktop mode, shall be done before `setmode` (SDL 1.2.10, and pygame 1.8.0)
        info = pygame.display.Info()

        pygame.display.set_caption(title)
        self.display_size = (info.current_w, info.current_h)
        self.surface = pygame.display.set_mode(self.__size, pygame.RESIZABLE)

    def update(self, events):
        """Update sprites according to Pygame events.

        :param events: list of events to process.
        :type events: list
        """
        pass

    def draw(self):
        """Draw all Sprites on surface and return updated Pygame rects.
        """
        return []

    def gui_eventloop(self, app_update):
        """Main GUI events loop (blocking).
        """
        fps = 40
        clock = pygame.time.Clock()

        while True:
            evts = list(pygame.event.get())

            if evtfilters.find_quit_event(evts):
                break

            # Update view elements according to user events
            self.update(evts)

            # Update application and plugins according to user events
            app_update(evts)

            # Draw view elements
            rects = self.draw()

            # Update dirty rects on screen
            pygame.display.update(rects)

            # Ensure the program will never run at more than <fps> frames per second
            clock.tick(fps)
