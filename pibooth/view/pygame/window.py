# -*- coding: utf-8 -*-

"""PygameWindow class to build a Pygame UI.
"""

import os
import sys
import pygame
import pygame_vkeyboard as vkb

from pibooth import evts
from pibooth.utils import LOGGER
from pibooth.view.base import BaseWindow, BaseScene
from pibooth.view.pygame import scenes, menu


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

    def set_scene(self, name):
        super(PygameWindow, self).set_scene(name)
        self._keyboard.disable()
        self._force_redraw = True

    def set_menu(self, app, cfg, pm):
        """Set the menu.
        """
        self._menu = menu.PygameMenu(app, cfg, pm, self._on_menu_event)
        self._menu.disable()

    def _create_scene(self, name):
        """Create scene instance."""
        return scenes.get_scene(name)

    def _on_keyboard_event(self, text):
        """Callback when new letter is typed on keyboard.

        :param text: new value
        :type text: str
        """
        if self._menu and self._menu.is_enabled():
            self._menu.set_text(text)

    def _on_menu_event(self, text):
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

    def toggle_menu(self):
        """Show/hide settings menu.
        """
        super(PygameWindow, self).toggle_menu()
        if self._menu:
            if self.is_menu_shown:
                self._menu.enable()
            else:
                self._menu.disable()
                self._force_redraw = True  # Because pygame-menu does not manage direty rects
        else:
            LOGGER.debug("[ESC] pressed. No menu configured -> exit")
            sys.exit(0)

    def update(self, events):
        """Update sprites according to Pygame events.

        :param events: list of events to process.
        :type events: list
        """
        for event in events:
            if event.type == pygame.VIDEORESIZE and not self.is_fullscreen:
                # Manual resizing
                self.surface = pygame.display.set_mode(event.size, pygame.RESIZABLE)
                self.resize(event.size)
                if self._menu and self._menu.is_enabled():
                    self._menu.resize(event.size)

            elif evts.is_fullscreen_event(event):
                self.toggle_fullscreen()
                self.resize(self.get_rect().size)
                if self._menu and self._menu.is_enabled():
                    self._menu.resize(self.get_rect().size)

            elif evts.is_button_print_event(event):
                # Convert HW button events to keyboard events for menu
                event = evts.create_click_event()
                LOGGER.debug("Generate MENU-APPLY event for menu")

            elif self._keyboard.is_enabled() and \
                    (event.type == pygame.MOUSEBUTTONDOWN and event.button in (1, 2, 3) or event.type == pygame.FINGERDOWN)\
                    and not self._keyboard.get_rect().collidepoint(evts.get_event_pos(self.display_size, event)):
                self._keyboard.disable()

            elif self._keyboard.is_enabled() and event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self._keyboard.disable()

            # Convert GUI events to pibooth events (plugins are based on them)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.toggle_menu()
                evts.post(evts.EVT_PIBOOTH_BTN_SETTINGS, is_shown=self.is_menu_shown)
                return  # Avoid menu.update() else it we be closed again by K_ESCAPE in the events list

            elif evts.is_fingers_event(event, 4):
                self.toggle_menu()
                evts.post(evts.EVT_PIBOOTH_BTN_SETTINGS, is_shown=self.is_menu_shown)

            elif event.type == pygame.KEYDOWN and event.key == pygame.K_c:
                evts.post_button_capture_event()

            elif event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                evts.post_button_print_event()

        self.scene.update(events)

        if self._keyboard.is_enabled():
            self._keyboard.update(events)
        elif self._menu and self._menu.is_enabled():
            self._menu.update(events)

    def draw(self):
        """Draw all Sprites on surface and return updated Pygame rects.
        """
        rects = self.scene.draw(self.surface, self._force_redraw)

        if self._menu and self._menu.is_enabled():
            rects += self._menu.draw(self.surface)

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
            #    it may update view elements internal variables
            app_update(events)

            # 2. Update view elements according to user events and re-create
            #    images for view elements which have changed
            self.update(events)

            # 3. Draw on buffer view elements which have changed
            rects = self.draw()

            # 4. Update dirty rects on screen (the most time-consuming action)
            pygame.display.update(rects)

            # 5. Ensure the program will never run at more than <fps> frames per second
            clock.tick(fps)
