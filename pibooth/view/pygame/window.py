# -*- coding: utf-8 -*-

import os
import pygame

from pibooth.view.base import BaseWindow


class PygameWindow(BaseWindow):

    """Class to create window using Pygame.
    """

    def __init__(self, title,
                 size=(800, 480),
                 bg_color=(0, 0, 0),
                 text_color=(255, 255, 255),
                 arrow_location=BaseWindow.ARROW_BOTTOM,
                 arrow_offset=0,
                 debug=False):
        super(PygameWindow, self).__init__(size, bg_color, text_color, arrow_location, arrow_offset, debug)

        # Prepare the pygame module for use
        if 'SDL_VIDEO_WINDOW_POS' not in os.environ:
            os.environ['SDL_VIDEO_CENTERED'] = '1'
        pygame.init()

        # Save the desktop mode, shall be done before `setmode` (SDL 1.2.10, and pygame 1.8.0)
        info = pygame.display.Info()

        pygame.display.set_caption(title)
        self.display_size = (info.current_w, info.current_h)
        self.surface = pygame.display.set_mode(self.__size, pygame.RESIZABLE)
