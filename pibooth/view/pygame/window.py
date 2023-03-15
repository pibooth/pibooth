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
from pibooth.view.pygame import menu


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
        super().__init__(size, background, text_color, arrow_location, arrow_offset, debug)

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
        super().set_scene(name)
        self._keyboard.disable()
        self._force_redraw = True

    def set_menu(self, app, cfg, pm):
        """Set the menu.
        """
        size = self.get_rect().size
        self._menu = menu.PygameMenu((size[0]*0.75, size[1]*0.75), app, cfg, pm, self._on_menu_closed)
        self._menu.disable()

    def _on_keyboard_event(self, text):
        """Callback when new letter is typed on keyboard.

        :param text: new value
        :type text: str
        """
        if self._menu and self._menu.is_enabled():
            self._menu.set_text(text)

    def _on_menu_closed(self):
        """Callback when menu is closed by graphical action on menu.
        """
        self.is_menu_shown = False
        self._force_redraw = True  # Because pygame-menu does not manage direty rects
        evts.post(evts.EVT_PIBOOTH_SETTINGS, menu_shown=self.is_menu_shown)

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

        size = self.get_rect().size
        self.resize(size)
        self.scene.update([])  # Do not acts on scenes, but recreate sprites with correct size
        if self._menu:
            self._menu.resize((size[0]*0.75, size[1]*0.75))

    def toggle_menu(self):
        """Show/hide settings menu.
        """
        if self._menu:
            super().toggle_menu()
            if self.is_menu_shown:
                self._menu.enable()
                evts.post(evts.EVT_PIBOOTH_SETTINGS, menu_shown=self.is_menu_shown)
            else:
                self._menu.disable()
                self._force_redraw = True  # Because pygame-menu does not manage direty rects
                evts.post(evts.EVT_PIBOOTH_SETTINGS, menu_shown=self.is_menu_shown)

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
                self.scene.update([])  # Do not acts on scenes, but recreate sprites with correct size
                if self._menu:
                    self._menu.resize((event.size[0]*0.75, event.size[1]*0.75))

            elif evts.is_fullscreen_event(event):
                self.toggle_fullscreen()

            elif event.type == menu.EVT_MENU_TEXT_EDIT:
                self._keyboard.enable()
                self._keyboard.set_text(event.text)

            elif self._keyboard.is_enabled() and \
                    (event.type == pygame.MOUSEBUTTONDOWN and event.button in (1, 2, 3) or event.type == pygame.FINGERDOWN)\
                    and not self._keyboard.get_rect().collidepoint(evts.get_event_pos(self.display_size, event)):
                self._keyboard.disable()

            elif self._keyboard.is_enabled() and event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self._keyboard.disable()

            elif ((event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE) or evts.is_fingers_event(event, 4))\
                    and not self.is_menu_shown:
                LOGGER.debug("Event triggered: KEY ESCAPE -> generate EVT_BUTTON_SETTINGS")
                evts.post(evts.EVT_BUTTON_SETTINGS)  # Use HW event to update sprites if necessary

            elif event.type == pygame.KEYDOWN and event.key == pygame.K_c:
                LOGGER.debug("Event triggered: KEY C -> generate EVT_BUTTON_CAPTURE")
                evts.post(evts.EVT_BUTTON_CAPTURE)  # Use HW event to update sprites if necessary

            elif event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                LOGGER.debug("Event triggered: KEY P -> generate EVT_BUTTON_PRINT")
                evts.post(evts.EVT_BUTTON_PRINT)  # Use HW event to update sprites if necessary

            elif event.type == evts.EVT_BUTTON_SETTINGS:
                if self._menu and self.is_menu_shown:
                    self._menu.back()
                elif self._menu:
                    self.toggle_menu()
                    return  # Avoid menu.update() else it we be closed again by K_ESCAPE in the events list
                else:
                    LOGGER.debug("[ESC] pressed. No menu configured -> exit")
                    sys.exit(0)

            elif event.type == evts.EVT_BUTTON_CAPTURE:
                if self.is_menu_shown:
                    self._menu.click()

            elif event.type == evts.EVT_BUTTON_PRINT:
                if self.is_menu_shown:
                    self._menu.next()

        if self._keyboard.is_enabled():
            # Events only acts on the keyboard
            self._keyboard.update(events)
        elif self._menu and self._menu.is_enabled():
            # Events only acts on the menu
            self._menu.update(events)
        else:
            self.scene.update(events)

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
