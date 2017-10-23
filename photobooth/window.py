# -*- coding: utf-8 -*-

import time
import pygame
from photobooth import pictures


class PtbWindow(object):

    """Manage the window.
    """

    def __init__(self, size):
        self.width, self.height = size
        self.surface = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        self.is_fullscreen = False

        self._counter = 0

    def show_intro(self):
        """Show introduction view.
        """
        self.surface.blit(pictures.get_image("intro.png"), (0, 0))
        pygame.display.update()

    def show_instructions(self):
        """Show instructions view.
        """
        self.surface.blit(pictures.get_image("instructions.png"), (0, 0))
        pygame.display.update()

    def show_counter(self, restart=False):
        """Show the next counter view.
        """
        if restart or self._counter > 4:  # Max 4 view
            self._counter = 0
        self._counter += 1
        self.surface.blit(pictures.get_image("pose{}.png".format(self._counter)), (0, 0))
        pygame.display.update()

    def show_wait(self):
        """Show wait view.
        """
        self.surface.blit(pictures.get_image("processing.png"), (0, 0))
        pygame.display.update()

    def show_finished(self):
        """Show finished view.
        """
        self.surface.blit(pictures.get_image("finished.png"), (0, 0))
        pygame.display.update()

    def show_image(self, pil_image):
        """Show a PIL image.
        """
        mode = pil_image.mode
        size = pil_image.size
        data = pil_image.tobytes()
        self.surface.blit(pygame.image.fromstring(data, size, mode), (0, 0))
        pygame.display.update()

    def show_image_from_file(self, image_file):
        """
        Show the merged file
        """
        self.surface.blit(pictures.get_image(image_file), (0, 0))
        pygame.display.update()

    def clear(self):
        """Clear the window content.
        """
        self.surface.fill((0, 0, 0))
        pygame.display.update()

    def toggle_fullscreen(self):
        """Set window to full screen.
        """
        if self.is_fullscreen:
            self.surface = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        else:
            self.surface = pygame.display.set_mode((self.width, self.height), pygame.FULLSCREEN)
        self.is_fullscreen = not self.is_fullscreen
