# -*- coding: utf-8 -*-

"""Pibooth config menu.
"""

import pygame
import pygame_menu as pgm
import pibooth
from pibooth import fonts
from pibooth.config.parser import DEFAULT


pgm.controls.KEY_BACK = pygame.K_ESCAPE
THEME = pgm.themes.THEME_GREEN.copy()
THEME.title_font = fonts.get_filename("Monoid-Retina")
THEME.widget_font = fonts.get_filename("Monoid-Retina")
THEME.widget_font_size = 20

SUBTHEME = THEME.copy()
SUBTHEME.widget_alignment = pgm.locals.ALIGN_LEFT
SUBTHEME.widget_offset = (40, 0)
SUBTHEME.widget_font_size = 18


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

    def __init__(self, window, config, onclose=None):
        self.window = window
        self.config = config
        self._main_menu = None
        self._close_callback = onclose

        size = self.window.get_rect().size
        self.size = (min(600, size[0]), min(400, size[1]))
        self._main_menu = pgm.Menu(self.size[1],
                                   self.size[0],
                                   "Settings",
                                   theme=THEME,
                                   onclose=self._on_close)

        self._main_menu.add_label('Pibooth version: {}'.format(pibooth.__version__))
        for name in ('GENERAL', 'WINDOW', 'PICTURE', 'PRINTER'):
            submenu = self._build_submenu(name)
            self._main_menu.add_button(submenu.get_title(), submenu)
        self._main_menu.add_button('Exit', pgm.events.EXIT)
        self._main_menu.disable()

    def _build_submenu(self, section):
        """Build sub-menu"""
        length = 0
        for name, option in DEFAULT[section].items():
            if option[2] and length < len(option[2]):
                length = len(option[2])
        pattern = '{:.<' + str(max(length + 2, 25)) + '} '

        menu = pgm.Menu(self.size[1],
                        self.size[0],
                        section.capitalize(),
                        theme=SUBTHEME)

        for name, option in DEFAULT[section].items():
            if option[2]:
                title = pattern.format(option[2])
                if isinstance(option[3], str):
                    menu.add_text_input(title,
                                        onchange=self._on_text_changed,
                                        default=self.config.get(section, name).strip('"'),
                                        # Parameters passed to callback:
                                        section=section,
                                        option=name)
                elif isinstance(option[3], (list, tuple)) and len(option[3]) == 3\
                        and all(isinstance(i, int) for i in option[3]):
                    menu.add_color_input(title,
                                         "rgb",
                                         default=self.config.gettyped(section, name),
                                         input_separator=',',
                                         onchange=self._on_color_changed,
                                         previsualization_width=1,
                                         # Parameters passed to callback:
                                         section=section,
                                         option=name)
                else:
                    values = [(v,) for v in option[3]]
                    menu.add_selector(title,
                                      values,
                                      onchange=self._on_selector_changed,
                                      default=_find(values, self.config.get(section, name)),
                                      # Parameters passed to callback:
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
            self.config.set(kwargs['section'], kwargs['option'], '"{}"'.format(str(value)))

    def _on_color_changed(self, value, **kwargs):
        """Called after each text input changed.
        """
        if self._main_menu.is_enabled():
            self.config.set(kwargs['section'], kwargs['option'], str(value))

    def _on_close(self):
        """Called when the menu is closed.
        """
        self._main_menu.disable()
        self.config.save()
        if self._close_callback:
            self._close_callback()

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
        if isinstance(self._main_menu.get_selected_widget(), pgm.widgets.Button):
            return pygame.event.Event(pygame.KEYDOWN, key=pgm.controls.KEY_APPLY,
                                      unicode='\r', mod=0, scancode=36,
                                      window=None, test=True)
        else:
            return pygame.event.Event(pygame.KEYDOWN, key=pgm.controls.KEY_RIGHT,
                                      unicode=u'\uf703', mod=0, scancode=124,
                                      window=None, test=True)

    def create_next_event(self):
        """Create a pygame event to select the next widget.
        """
        return pygame.event.Event(pygame.KEYDOWN, key=pgm.controls.KEY_MOVE_UP,
                                  unicode=u'\uf701', mod=0, scancode=125,
                                  window=None, test=True)

    def create_back_event(self):
        """Create a pygame event to back to the previous menu.
        """
        return pygame.event.Event(pygame.KEYDOWN, key=pgm.controls.KEY_BACK,
                                  unicode=u'\x1b', mod=0, scancode=53,
                                  window=None, test=True)

    def process(self, events):
        """Process the events related to the menu.
        """
        self._main_menu.update(events)
        if self.is_shown():  # Menu may have been closed
            self._main_menu.draw(self.window.surface)
