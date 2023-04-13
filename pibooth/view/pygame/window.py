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
from pibooth.view.pygame import menu, sprites


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
        self.background_sprite = sprites.ImageSprite(size=size)
        self.set_background(self.bg_color_or_path)
        self.statusbar_sprite = sprites.StatusBarSprite(size=(50, 50))

        self._keyboard = vkb.VKeyboard(self.surface,
                                       self._on_keyboard_event,
                                       vkb.VKeyboardLayout(vkb.VKeyboardLayout.QWERTY),
                                       renderer=vkb.VKeyboardRenderer.DARK,
                                       show_text=True,
                                       joystick_navigation=True)
        self._keyboard.disable()
        self._menu = None
        self._force_redraw = False

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

    def add_scene(self, scene):
        """Override parent class to add common sprites.
        """
        super().add_scene(scene)
        scene.add_sprite(self.background_sprite, False, layer=0)
        scene.add_sprite(self.statusbar_sprite, False)

    def set_scene(self, name):
        """Override parent class to hide keyboard and full redraw scene.
        """
        super().set_scene(name)
        self.set_background(self.bg_color_or_path)
        self._keyboard.disable()
        self._force_redraw = True

    def set_menu(self, app, cfg, pm):
        """Set the menu.
        """
        size = self.get_rect().size
        self._menu = menu.PygameMenu((min(size[0]*0.75, 600), size[1]*0.75), app, cfg, pm, self._on_menu_closed)
        self._menu.disable()

    def set_background(self, color_or_path):
        """Set background sprite.

        :param color_or_path: color of path to an image
        :type color_or_path: tuple or str
        """
        self.background_sprite.set_rect(*self.get_rect())
        self.background_sprite.set_skin(color_or_path)
        self.background_sprite.set_crop()

    def set_system_status(self, printer_queue_size=None, printer_failure=None, total_printed=None, total_taken=None):
        """Set system status.
        """
        if printer_queue_size is not None:
            self.statusbar_sprite.set_printer_queue(printer_queue_size)
        if printer_failure is not None:
            self.statusbar_sprite.set_printer_failure(printer_failure)
        if total_printed is not None:
            self.statusbar_sprite.set_printed_counter(total_printed)
        if total_taken is not None:
            self.statusbar_sprite.set_taken_counter(total_taken)

    def resize(self, size):
        """Resize common spritees, then scenes.
        """
        if not self.is_fullscreen:
            self._size = size  # Size of the window when not fullscreen

        # Call get_rect() to take new computed size if != self._size
        self.background_sprite.set_rect(*self.get_rect())
        width, height = self.get_rect().width // 20, self.get_rect().height * 2 // 5
        self.statusbar_sprite.set_rect(0, self.get_rect().height - height, width, height)
        if self.scene:
            self.scene.resize(self.get_rect().size)
            self.scene.update([])  # Do not acts on scene, but recreate sprites with correct size

    def get_rect(self, absolute=False):
        """Return a Rect object (as defined in pygame) for this window.

        :param absolute: absolute position considering the window centered on screen
        :type absolute: bool
        """
        if absolute:
            if 'SDL_VIDEO_WINDOW_POS' in os.environ:
                posx, posy = [int(v) for v in os.environ['SDL_VIDEO_WINDOW_POS'].split(',')]
                return self.surface.get_rect(x=posx, y=posy)
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
        if self._menu:
            self._menu.resize((min(size[0]*0.75, 600), size[1]*0.75))

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
                if self._menu:
                    self._menu.resize((min(event.size[0]*0.75, 600), event.size[1]*0.75))

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
        if self.scene and (not self._menu or not self._menu.is_enabled()):
            self.scene.update(events)

    def draw(self):
        """Draw all Sprites on surface and return updated Pygame rects.
        """
        rects = []

        if self.scene and (not self._menu or not self._menu.is_enabled()):
            rects += self.scene.draw(self.surface, self._force_redraw)

        rects += self._keyboard.draw(self.surface, self._force_redraw)

        if not self._keyboard.is_enabled() and self._menu and self._menu.is_enabled():
            rects += self._menu.draw(self.surface)

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
