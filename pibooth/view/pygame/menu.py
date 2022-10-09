# -*- coding: utf-8 -*-

"""Pibooth config menu.
"""

import pygame
import pygame_menu as pgm
import pibooth
from pibooth import fonts
from pibooth.utils import LOGGER
from pibooth.config.default import DEFAULT


pgm.controls.KEY_BACK = pygame.K_ESCAPE

THEME_WHITE = pgm.themes.Theme(
    background_color=(255, 255, 255),
    scrollbar_thick=14,
    scrollbar_slider_pad=2,
    scrollbar_slider_color=(35, 149, 135),
    selection_color=(29, 120, 107),
    title_background_color=(35, 149, 135),
    title_font=fonts.get_filename("Monoid-Regular"),
    title_font_size=33,
    title_font_color=(255, 255, 255),
    widget_margin=(0, 20),
    widget_font=fonts.get_filename("Monoid-Retina"),
    widget_font_size=30,
    widget_font_color=(0, 0, 0),
)

SUBTHEME1_WHITE = THEME_WHITE.copy()
SUBTHEME1_WHITE.background_color = (255, 255, 255)
SUBTHEME1_WHITE.scrollbar_slider_color = (252, 151, 0)
SUBTHEME1_WHITE.selection_color = (241, 125, 1)
SUBTHEME1_WHITE.title_background_color = (252, 151, 0)
SUBTHEME1_WHITE.widget_alignment = pgm.locals.ALIGN_LEFT
SUBTHEME1_WHITE.widget_margin = (40, 10)
SUBTHEME1_WHITE.widget_font_size = 18

SUBTHEME2_WHITE = SUBTHEME1_WHITE.copy()
SUBTHEME2_WHITE.scrollbar_slider_color = (152, 43, 175)
SUBTHEME2_WHITE.selection_color = (120, 36, 161)
SUBTHEME2_WHITE.title_background_color = (152, 43, 175)
SUBTHEME2_WHITE.widget_alignment = pgm.locals.ALIGN_CENTER
SUBTHEME2_WHITE.widget_margin = (0, 20)

THEME_DARK = THEME_WHITE.copy()
THEME_DARK.background_color = (40, 41, 35)
THEME_DARK.cursor_color = (255, 255, 255)
THEME_DARK.widget_font_color = (255, 255, 255)

SUBTHEME1_DARK = SUBTHEME1_WHITE.copy()
SUBTHEME1_DARK.background_color = (40, 41, 35)
SUBTHEME1_DARK.cursor_color = (255, 255, 255)
SUBTHEME1_DARK.widget_font_color = (255, 255, 255)

SUBTHEME2_DARK = SUBTHEME2_WHITE.copy()
SUBTHEME2_DARK.background_color = (40, 41, 35)
SUBTHEME2_DARK.cursor_color = (255, 255, 255)
SUBTHEME2_DARK.widget_font_color = (255, 255, 255)


def _find(choices, value):
    """Find index for the given value in choices.
    """
    i = 0
    for val in choices:
        if val[0] == value:
            return i
        i += 1
    return 0


def _counters(counters):
    """Return the formatted text for counters.
    """
    long_name = max(counters.names(), key=len)
    pattern = '{:.<' + str(max(len(long_name) + 2, 25)) + '} {: >4}'
    return [pattern.format(name.replace("_", " ").capitalize(), counters[name]) for name in counters]


class PygameMenu(object):

    def __init__(self, application, configuration, callback=None):
        self.app = application
        self.cfg = configuration
        self.callback = callback
        self.size = (600, 400)
        self._changed = False
        self._main_menu = pgm.Menu(title="Settings v{}".format(pibooth.__version__),
                                   width=self.size[0],
                                   height=self.size[1],
                                   theme=THEME_DARK,
                                   touchscreen=True,
                                   onclose=self.on_close)
        self._main_menu.add.vertical_margin(20)

        for name in DEFAULT:
            submenu = self._build_submenu(name)
            if len(submenu._widgets) > 2:
                self._main_menu.add.button(submenu.get_title(), submenu)
        self._main_menu.add.button('Exit', self.on_exit)
        self._main_menu.add.vertical_margin(20)

    def _build_submenu(self, section):
        """Build sub-menu"""
        length = 0
        for name, option in DEFAULT[section].items():
            if option[2] and length < len(option[2]):
                length = len(option[2])
        pattern = '{:.<' + str(max(length + 2, 25)) + '} '

        menu = pgm.Menu(title=section.capitalize(),
                        width=self.size[0],
                        height=self.size[1],
                        theme=SUBTHEME1_DARK,
                        touchscreen=True)
        menu.add.vertical_margin(20)

        for name, option in DEFAULT[section].items():
            if option[2]:
                title = pattern.format(option[2])
                if isinstance(option[3], str):
                    menu.add.text_input(title,
                                        onchange=self.on_text_changed,
                                        default=self.cfg.get(section, name).strip('"'),
                                        # Parameters passed to callback:
                                        section=section,
                                        option=name)
                elif isinstance(option[3], (list, tuple)) and len(option[3]) == 3\
                        and all(isinstance(i, int) for i in option[3]):
                    menu.add.color_input(title,
                                         "rgb",
                                         default=self.cfg.gettyped(section, name),
                                         input_separator=',',
                                         onchange=self.on_color_changed,
                                         previsualization_width=1,
                                         # Parameters passed to callback:
                                         section=section,
                                         option=name)
                else:
                    values = [(v,) for v in option[3]]
                    menu.add.selector(title,
                                      values,
                                      onchange=self.on_selector_changed,
                                      default=_find(values, self.cfg.get(section, name)),
                                      # Parameters passed to callback:
                                      section=section,
                                      option=name)

        if section.lower() == 'general':
            menu.add.vertical_margin(40)
            menu.add.button("View counters",
                            self._build_submenu_counters("Counters"),
                            margin=(self.size[0] // 2 - 100, 0))
            menu.add.vertical_margin(20)
            if self.pm.list_external_plugins():
                menu.add.button("Manage plugins",
                                self._build_submenu_plugins("Plugins"),
                                margin=(self.size[0] // 2 - 105, 0))

        menu.add.vertical_margin(20)
        return menu

    def _build_submenu_counters(self, title):
        menu = pgm.Menu(title=title.capitalize(),
                        width=self.size[0],
                        height=self.size[1],
                        theme=SUBTHEME2_DARK,
                        touchscreen=True)
        labels = []
        for text in _counters(self.app.count):
            labels.append(menu.add.label(text))
        menu.add.vertical_margin(40)
        menu.add.button("Reset all", self.on_counters_reset, labels)
        return menu

    def _build_submenu_plugins(self, title):
        menu = pgm.Menu(title=title.capitalize(),
                        width=self.size[0],
                        height=self.size[1],
                        theme=SUBTHEME2_DARK,
                        touchscreen=True)

        plugins = self.pm.list_external_plugins()
        long_name = max([self.pm.get_friendly_name(p) for p in plugins], key=len)
        pattern = '{:.<' + str(max(len(long_name) + 2, 25)) + '}'

        for plugin in plugins:
            enabled = self.pm.is_registered(plugin)
            menu.add.toggle_switch(pattern.format(self.pm.get_friendly_name(plugin)),
                                   enabled,
                                   state_color=((178, 178, 178), SUBTHEME2_DARK.title_background_color),
                                   onchange=self.on_plugin_toggled,
                                   # Parameters passed to callback:
                                   section='GENERAL',
                                   option='plugins_disabled',
                                   plugin=plugin)
        return menu

    def on_keyboard_event(self, text):
        """Called after each option changed.
        """
        if self._main_menu.is_enabled():  # Menu may have been closed
            selected = self._main_menu.get_current().get_selected_widget()
            if isinstance(selected, pgm.widgets.TextInput):
                if isinstance(selected, pgm.widgets.ColorInput):
                    try:
                        selected.set_value(tuple([int(c) for c in text.split(',')]))
                    except Exception as ex:
                        LOGGER.error("Invalid color value '%s' (%s)", text, ex)
                else:
                    selected.set_value(text)
                selected.change()

    def on_selector_changed(self, value, **kwargs):
        """Called after each option changed.
        """
        if self._main_menu.is_enabled():  # Menu may have been closed
            self.cfg.set(kwargs['section'], kwargs['option'], str(value[0][0]))
            self._changed = True

    def on_text_changed(self, value, **kwargs):
        """Called after each text input changed.
        """
        if self._main_menu.is_enabled():  # Menu may have been closed
            self.cfg.set(kwargs['section'], kwargs['option'], '"{}"'.format(str(value)))
            self._changed = True

    def on_color_changed(self, value, **kwargs):
        """Called after each text input changed.
        """
        if self._main_menu.is_enabled():  # Menu may have been closed
            self.cfg.set(kwargs['section'], kwargs['option'], str(value))
            self._changed = True

    def on_counters_reset(self, labels):
        """Called when the counters are reset.
        """
        self.app.count.reset()
        for label, text in zip(labels, _counters(self.app.count)):
            label.set_title(text)

    def on_plugin_toggled(self, activated, **kwargs):
        """Called when a plugin active state is toggled.
        """
        plugin = kwargs['plugin']
        disabled = self.cfg.gettuple(kwargs['section'], kwargs['option'], str)
        if activated and not self.pm.is_registered(plugin):
            self.pm.register(plugin)
            plugin_name = self.pm.get_name(plugin)
            disabled = tuple([name for name in disabled if plugin_name != name])
            self._changed = True

            # Because no hook is called for plugins disabled at pibooth startup, need to
            # ensure that mandatory hooks have been called when enabling a plugin
            if 'pibooth_configure' not in self.pm.get_calls_history(plugin):
                hook = self.pm.subset_hook_caller_for_plugin('pibooth_configure', plugin)
                hook(cfg=self.cfg)
            if 'pibooth_startup' not in self.pm.get_calls_history(plugin):
                hook = self.pm.subset_hook_caller_for_plugin('pibooth_startup', plugin)
                hook(cfg=self.cfg, app=self.app)

        elif not activated and self.pm.is_registered(plugin):
            plugin_name = self.pm.get_name(plugin)
            self.pm.unregister(plugin)
            if plugin_name not in disabled:
                disabled += (plugin_name,)
                self._changed = True

        if not disabled:
            disabled = ''
        self.cfg.set(kwargs['section'], kwargs['option'], str(disabled))

    def on_close(self):
        """Called when the menu is closed.
        """
        self._main_menu.disable()
        if self._changed:
            self.cfg.save()
            self._changed = False

    def on_exit(self):
        """Called when the application is exited by menu.
        """
        self.on_close()
        exit(0)

    def enable(self):
        """Show the menu.
        """
        self._main_menu.enable()

    def disable(self):
        """Show the menu.
        """
        self._main_menu.disable()

    def is_enabled(self):
        """Return True if the menu is shown.
        """
        return self._main_menu.is_enabled()

    def resize(self, size):
        self._main_menu.resize(size[0], size[1])

    def update(self, events):
        """Process the events related to the menu.
        """
        self._main_menu.update(events)
        if self._main_menu.is_enabled():  # Menu may have been closed
            selected = self._main_menu.get_current().get_selected_widget()
            if isinstance(selected, pgm.widgets.TextInput) and self.cfg.getboolean('GENERAL', 'vkeyboard'):
                for event in events:
                    if (event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.FINGERDOWN)\
                            and selected.get_scrollarea().collide(selected, event):
                        self._keyboard.enable()
                        if isinstance(selected, pgm.widgets.ColorInput):
                            self._keyboard.set_text(",".join([str(c) for c in selected.get_value()]))
                        else:
                            self._keyboard.set_text(selected.get_value())
                        return

    def draw(self, surface):
        return self._main_menu.draw(surface)
