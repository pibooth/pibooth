# -*- coding: utf-8 -*-

"""PygameWindow class to build a Pygame UI.
"""

import os
import pygame
import pygame_vkeyboard as vkb

from pibooth import evtfilters
from pibooth.utils import LOGGER
from pibooth.view.base import BaseWindow
from pibooth.view.pygame import scenes


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
        self.surface = pygame.display.set_mode(self._size, pygame.RESIZABLE)

        self._keyboard = vkb.VKeyboard(self.surface,
                                       self._on_keyboard_event,
                                       vkb.VKeyboardLayout(vkb.VKeyboardLayout.QWERTY),
                                       renderer=vkb.VKeyboardRenderer.DARK,
                                       show_text=True,
                                       joystick_navigation=True)
        self._keyboard.disable()

    def _create_scene(self, name):
        """Create scene instance."""
        return scenes.get_scene(name)

    def _on_keyboard_event(self, text):
        print(text)

    def get_rect(self, absolute=False):
        """Return a Rect object (as defined in pygame) for this window.

        :param absolute: absolute position considering the window centered on screen
        :type absolute: bool
        """
        if absolute:
            return self.surface.get_rect(center=(self.display_size[0] / 2, self.display_size[1] / 2))
        return self.surface.get_rect()

    def resize(self, size):
        """Resize the window keeping aspect ratio.
        """
        if not self.is_fullscreen:
            self._size = size  # Manual resizing
            self.surface = pygame.display.set_mode(self._size, pygame.RESIZABLE)

    def toggle_fullscreen(self):
        """Set window to full screen or initial size.
        """
        if self.is_fullscreen:
            self.is_fullscreen = False  # Set before resize
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            self.surface = pygame.display.set_mode(self._size, pygame.RESIZABLE)
        else:
            self.is_fullscreen = True  # Set before resize
            # Make an invisible cursor (don't use pygame.mouse.set_visible(False) because
            # the mouse event will always return the window bottom-right coordinate)
            pygame.mouse.set_cursor((8, 8), (0, 0), (0, 0, 0, 0, 0, 0, 0, 0), (0, 0, 0, 0, 0, 0, 0, 0))
            self.surface = pygame.display.set_mode(self.display_size, pygame.FULLSCREEN)

    def update(self, events):
        """Update sprites according to Pygame events.

        :param events: list of events to process.
        :type events: list
        """
        for event in events:
            if evtfilters.is_resize_event(event):
                self.resize(event.size)
            elif evtfilters.is_fullscreen_event(event):
                self.toggle_fullscreen()
            elif evtfilters.is_settings_event(event):
                self.toggle_menu()
            elif evtfilters.is_print_button_event(event, self):
                # Convert HW button events to keyboard events for menu
                event = evtfilters.create_click_event()
                LOGGER.debug("EVT_BUTTONDOWN: generate MENU-APPLY event")
                events += (event,)

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
