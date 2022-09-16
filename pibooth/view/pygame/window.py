# -*- coding: utf-8 -*-

"""PygameWindow class to build a Pygame UI.
"""

import os
import pygame
import pygame_vkeyboard as vkb

from pibooth import evtfilters
from pibooth.utils import LOGGER
from pibooth.view.base import BaseWindow, BaseScene
from pibooth.view.pygame import scenes


class PygameWindow(BaseWindow):

    """Class to create window using Pygame.
    """

    def __init__(self, title,
                 size=(800, 480),
                 background=(0, 0, 0),
                 text_color=(255, 255, 255),
                 arrow_location=BaseScene.ARROW_BOTTOM,
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

        self._menu = None

        self._force_redraw = False

    def _create_scene(self, name):
        """Create scene instance."""
        return scenes.get_scene(name)

    def set_scene(self, name):
        super(PygameWindow, self).set_scene(name)
        self.scene.resize(self.get_rect().size)
        self._keyboard.disable()
        self._force_redraw = True

    def _on_keyboard_event(self, text):
        print(text)

    def get_rect(self, absolute=False):
        """Return a Rect object (as defined in pygame) for this window.

        :param absolute: absolute position considering the window centered on screen
        :type absolute: bool
        """
        if absolute:
            if 'SDL_VIDEO_WINDOW_POS' in os.environ:
                posx, posy = [int(v) for v in os.environ['SDL_VIDEO_WINDOW_POS'].split(',')]
                return self.surface.get_rect(x=posx, y=posy)
            else:
                return self.surface.get_rect(center=(self.display_size[0] / 2, self.display_size[1] / 2))
        return self.surface.get_rect()

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
            if event.type == pygame.VIDEORESIZE and not self.is_fullscreen:
                self._size = event.size  # Manual resizing
                self.surface = pygame.display.set_mode(self._size, pygame.RESIZABLE)
                self.scene.resize(self.get_rect().size)

            elif evtfilters.is_fullscreen_event(event):
                self.toggle_fullscreen()
                self.scene.resize(self.get_rect().size)

            elif evtfilters.is_settings_event(event):
                self.toggle_menu()

            elif evtfilters.is_print_button_event(event):
                # Convert HW button events to keyboard events for menu
                event = evtfilters.create_click_event()
                LOGGER.debug("Generate MENU-APPLY event for menu")
                events += (event,)

            # Convert GUI events to pibooth events (plugins are based on them)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                evtfilters.post(evtfilters.EVT_PIBOOTH_BTN_SETTINGS, is_shown=self._menu.is_shown())

            elif evtfilters.is_fingers_event(event, 4):
                evtfilters.post(evtfilters.EVT_PIBOOTH_BTN_SETTINGS, is_shown=self._menu.is_shown())

            elif event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
                evtfilters.post_capture_button_event()

            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
                evtfilters.post_print_button_event()

        self.scene.update(events)

        if self._keyboard.is_enabled():
            self._keyboard.update(events)

    def draw(self):
        """Draw all Sprites on surface and return updated Pygame rects.
        """
        rects = self.scene.draw(self.surface, self._force_redraw)

        if self._keyboard.is_enabled():
            rects += self._keyboard.draw(self.surface, self._force_redraw)

        self._force_redraw = False
        return rects

    def eventloop(self, app_update):
        """Main GUI events loop (blocking).
        """
        fps = 25
        clock = pygame.time.Clock()

        while True:
            events = list(pygame.event.get())

            # 0. Check if exit request
            for event in events:
                if event.type == pygame.QUIT:
                    return

            # 1. Update application and plugins according to user events,
            #    they may have updated view elements
            app_update(events)

            # 2. Update view elements according to user events and re-create
            #    images for view elements which have changed
            self.update(events)

            # 3. Draw on buffer view elements which have changed
            rects = self.draw()
            if rects:
                print(rects)

            # 4. Update dirty rects on screen (the most time-consuming action)
            pygame.display.update(rects)

            # 5. Ensure the program will never run at more than <fps> frames per second
            clock.tick(fps)
