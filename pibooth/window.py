# -*- coding: utf-8 -*-

import pygame
from pibooth import pictures


class PtbWindow(object):

    """Manage the window.
    """

    def __init__(self, size):
        self.width, self.height = size
        pygame.display.set_caption('Pibooth')
        self.surface = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        self.is_fullscreen = False

        self._counter = 0
        self._current_frame = None

    def _show_and_memorize(self, image_name):
        """Show image and memorize an image. If the image is the same
        as the current displayed, nothing is done.
        """
        if self._current_frame != image_name:
            self.surface.blit(pictures.get_image(image_name), (0, 0))
            pygame.display.update()
            self._current_frame = image_name

    def show_intro(self):
        """Show introduction view.
        """
        self._show_and_memorize("intro.png")

    def show_instructions(self):
        """Show instructions view.
        """
        self._show_and_memorize("instructions.png")

    def show_counter(self, restart=False):
        """Show the next counter view.
        """
        if restart or self._counter > 4:  # Max 4 view
            self._counter = 0
        self._counter += 1
        self._show_and_memorize("pose{}.png".format(self._counter))

    def show_wait(self):
        """Show wait view.
        """
        self._show_and_memorize("processing.png")

    def show_finished(self):
        """Show finished view.
        """
        self._show_and_memorize("finished.png")

    def show_image(self, pil_image):
        """Show a PIL image.
        """
        mode = pil_image.mode
        size = pil_image.size
        data = pil_image.tobytes()
        self.surface.blit(pygame.image.fromstring(data, size, mode), (0, 0))
        pygame.display.update()
        self._current_frame = None

    def show_image_from_file(self, image_file):
        """
        Show the merged file
        """
        self.surface.blit(pictures.get_image(image_file), (0, 0))
        pygame.display.update()
        self._current_frame = None

    def clear(self):
        """Clear the window content.
        """
        self.surface.fill((0, 0, 0))
        pygame.display.update()
        self._current_frame = None

    def toggle_fullscreen(self):
        """Set window to full screen.
        """
        if self.is_fullscreen:
            self.surface = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        else:
            self.surface = pygame.display.set_mode((self.width, self.height), pygame.FULLSCREEN)
        self.is_fullscreen = not self.is_fullscreen
