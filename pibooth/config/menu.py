# -*- coding: utf-8 -*-

"""Pibooth config menu.
"""

import pygameMenu as pgm
from pygameMenu import locals as pgmloc
from pygameMenu import fonts as pgmfonts
from pibooth.config.parser import DEFAULT


def _find(choices, value):
    """Find index for the given value in choices.
    """
    i = 0
    for _, val in choices:
        if val == value:
            return i
        i += 1
    return 0


class PiConfigMenu(object):

    def __init__(self, surface, config):
        self.surface = surface
        self.config = config

        width = self.surface.get_rect().width
        height = self.surface.get_rect().height

        self._main_menu = pgm.Menu(surface,
                                   width,
                                   height,
                                   pgmfonts.FONT_FRANCHISE,
                                   'Settings',
                                   draw_region_y=55,
                                   menu_color=(0, 75, 100),
                                   menu_color_title=(120, 45, 30),
                                   bgfun=lambda: self.surface.fill((40, 0, 40)),
                                   enabled=False,
                                   onclose=self.config.save
                                   )

        for name in ('GENERAL', 'WINDOW', 'PICTURE', 'PRINTER'):
            submenu = self._build_submenu(name, width, height)
            self._main_menu.add_option(submenu.get_title(), submenu)
        self._main_menu.add_option('Exit Pibooth', pgmloc.PYGAME_MENU_EXIT)

    def _build_submenu(self, section, width, height):
        """Build submenu"""
        menu = pgm.TextMenu(self.surface,
                            width,
                            height,
                            pgmfonts.FONT_FRANCHISE,
                            section.capitalize(),
                            font_size=30,
                            draw_region_y=45,
                            menu_color=(0, 50, 100),
                            menu_color_title=(120, 45, 30),
                            bgfun=lambda: self.surface.fill((40, 0, 40)),
                            )

        for name, option in DEFAULT[section].items():
            if option[2]:
                values = [(v, v) for v in option[3]]
                menu.add_selector(option[2],
                                  values,
                                  onchange=self._on_option_changed,
                                  onreturn=None,
                                  default=_find(values, self.config.get(section, name)),
                                  # Additional parameters:
                                  section=section,
                                  option=name)

        return menu

    def _on_option_changed(self, value, **kwargs):
        """Called after each option changed.
        """
        if self._main_menu.is_enabled():
            self.config.set(kwargs['section'], kwargs['option'], str(value))

    def show(self):
        """Show the menu.
        """
        self._main_menu.enable()

    def process(self, events):
        """Process the events related to the menu.
        """
        self._main_menu.mainloop(events)
