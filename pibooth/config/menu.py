# -*- coding: utf-8 -*-

"""Pibooth config menu.
"""

import pygame
import pygameMenu as pgm
from pygameMenu import controls as pgmctrl
from pygameMenu import events as pgmevt
from pibooth import fonts
from pibooth.config.parser import DEFAULT


pgmctrl.KEY_BACK = pygame.K_ESCAPE


def _find(choices, value):
    """Find index for the given value in choices.
    """
    i = 0
    for val in choices:
        if val[0] == value:
            return i
        i += 1
    return 0


class PiConfigMenu(object):

    def __init__(self, window, config, fps):
        self.window = window
        self.config = config
        self._main_menu = None

        width = self.window.get_rect().width
        height = self.window.get_rect().height

        self._main_menu = pgm.Menu(self.window.surface,
                                   width,
                                   height,
                                   fonts.get_filename("Amatic-Bold"),
                                   'Settings',
                                   draw_region_y=55,
                                   font_color=(38, 139, 210),
                                   color_selected=(42, 161, 152),
                                   menu_color=(253, 246, 227),
                                   menu_color_title=(238, 232, 213),
                                   enabled=False,
                                   onclose=self._on_close,
                                   dopause=False,
                                   )

        for name in ('GENERAL', 'WINDOW', 'PICTURE', 'PRINTER'):
            submenu = self._build_submenu(name, width, height)
            self._main_menu.add_option(submenu.get_title(), submenu)
        self._main_menu.add_option('Exit Pibooth', pgmevt.EXIT)

        self._main_menu.set_fps(fps)

    def _build_submenu(self, section, width, height):
        """Build sub-menu"""
        menu = pgm.Menu(self.window.surface,
                        width,
                        height,
                        fonts.get_filename("Amatic-Bold"),
                        section.capitalize(),
                        font_size=30,
                        font_color=(133, 153, 0),
                        color_selected = (203, 75, 22),
                        menu_color = (253, 246, 227),
                        menu_color_title = (238, 232, 213),
                        dopause=False,
                        )

        for name, option in DEFAULT[section].items():
            if option[2]:
                if isinstance(option[3], str):
                    menu.add_text_input(option[2],
                                        onchange=self._on_text_changed,
                                        default=self.config.get(section, name),
                                        # Additional parameters:
                                        section=section,
                                        option=name)
                else:
                    values = [(v,) for v in option[3]]
                    menu.add_selector(option[2],
                                      values,
                                      onchange=self._on_selector_changed,
                                      default=_find(values, self.config.get(section, name)),
                                      # Additional parameters:
                                      section=section,
                                      option=name)

        return menu

    def _on_selector_changed(self, value, **kwargs):
        """Called after each option changed.
        """
        if self._main_menu.is_enabled():
            self.config.set(kwargs['section'], kwargs['option'], str(value[0]))

    def _on_text_changed(self, value, **kwargs):
        """Called after each text input changed.
        """
        if self._main_menu.is_enabled():
            self.config.set(kwargs['section'], kwargs['option'], str(value))

    def _on_close(self):
        """Called when the menu is closed.
        """
        self._main_menu.disable()
        self.config.save()

    def get_selected_widget(self):
        """
        Return the currently selected widget.

        :return: Widget object
        :rtype: pygameMenu.widgets.widget.Widget
        """
        return self._main_menu._top._actual._option[self._main_menu._top._actual._index]

    def show(self):
        """Show the menu.
        """
        self._main_menu.enable()

    def is_shown(self):
        """Return True if the menu is shown.
        """
        return self._main_menu.is_enabled()

    def create_click_event(self):
        """Create a pygame event to click on the currently selected
        widget on the menu. If the widget is a button, ENTER event
        is created, else LEFT event is created.
        """
        if isinstance(self.get_selected_widget(), pgm.widgets.Button):
            return pygame.event.Event(pygame.KEYDOWN, key=pgmctrl.KEY_APPLY,
                                      unicode='\r', mod=0, scancode=36,
                                      window=None, test=True)
        else:
            return pygame.event.Event(pygame.KEYDOWN, key=pgmctrl.KEY_RIGHT,
                                      unicode='\uf703', mod=0, scancode=124,
                                      window=None, test=True)

    def create_next_event(self):
        """Create a pygame event to select the next widget.
        """
        return pygame.event.Event(pygame.KEYDOWN, key=pgmctrl.KEY_MOVE_UP,
                                  unicode='\uf701', mod=0, scancode=125,
                                  window=None, test=True)

    def create_back_event(self):
        """Create a pygame event to back to the previous menu.
        """
        return pygame.event.Event(pygame.KEYDOWN, key=pgmctrl.KEY_BACK,
                                  unicode='\x1b', mod=0, scancode=53,
                                  window=None, test=True)

    def process(self, events):
        """Process the events related to the menu.
        """
        self._main_menu.mainloop(events)  # block until exit menu (dopause=True)
