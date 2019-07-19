# -*- coding: utf-8 -*-

"""Pibooth config menu.
"""

import pygame
import pygameMenu as pgm
from pygameMenu import config_controls
from pygameMenu import events as pgmevt
from pygameMenu import fonts as pgmfonts
from pibooth.config.parser import DEFAULT


config_controls.MENU_CTRL_BACK = pygame.K_ESCAPE


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

    def __init__(self, window, config):
        self.window = window
        self.config = config
        self._main_menu = None

        width = self.window.get_rect().width
        height = self.window.get_rect().height

        self._main_menu = pgm.Menu(self.window.surface,
                                   width,
                                   height,
                                   pgmfonts.FONT_FRANCHISE,
                                   'Settings',
                                   draw_region_y=55,
                                   menu_alpha=80,
                                   menu_color=(0, 75, 100),
                                   menu_color_title=(120, 45, 30),
                                   enabled=False,
                                   option_shadow=True,
                                   onclose=self.config.save,
                                   dopause=False,
                                   bgfun=None
                                   )

        for name in ('GENERAL', 'WINDOW', 'PICTURE', 'PRINTER'):
            submenu = self._build_submenu(name, width, height)
            self._main_menu.add_option(submenu.get_title(), submenu)
        self._main_menu.add_option('Exit Pibooth', pgmevt.PYGAME_MENU_EXIT)

    def _build_submenu(self, section, width, height):
        """Build sub-menu"""
        menu = pgm.TextMenu(self.window.surface,
                            width,
                            height,
                            pgmfonts.FONT_FRANCHISE,
                            section.capitalize(),
                            font_size=30,
                            draw_region_y=45,
                            menu_alpha=90,
                            option_shadow=True,
                            menu_color=(0, 50, 100),
                            menu_color_title=(120, 45, 30),
                            dopause=False
                            )

        for name, option in DEFAULT[section].items():
            if option[2]:
                if isinstance(option[3], str):
                    menu.add_text_input(option[2],
                                        onchange=self._on_text_changed,
                                        default=self.config.get(section, name),
                                        maxsize=20,
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
        """Called after each option changed.
        """
        if self._main_menu.is_enabled():
            self.config.set(kwargs['section'], kwargs['option'], str(value))

    def show(self):
        """Show the menu.
        """
        self._main_menu.enable()

    def is_shown(self):
        """Return True if the menu is shown.
        """
        return self._main_menu.is_enabled()

    def process(self, events):
        """Process the events related to the menu.
        """
        self._main_menu.mainloop(events)  # block until exit menu (dopause=True)
