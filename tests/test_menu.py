# -*- coding: utf-8 -*-

import pytest
import pygame
import pygame_menu as pgm
from pibooth import language
from pibooth import printer as printer_module
from pibooth.counters import Counters
from pibooth.printer import Printer
from pibooth.plugins import create_plugin_manager
from pibooth.config.parser import PiConfigParser
from pibooth.config.menu import PiConfigMenu, _MenuSurface
from pibooth.view.window import PiWindow


class ApplicationMock:

    def __init__(self, tmpdir, printer):
        self.count = Counters(str(tmpdir.join('counters.json')), taken=0, printed=0, forgotten=0)
        self.printer = printer
        self.enabled = []
        self.disabled = []

    def enable_plugin(self, plugin):
        self.enabled.append(plugin)

    def disable_plugin(self, plugin):
        self.disabled.append(plugin)


@pytest.fixture
def menu(tmpdir, printer):
    pm = create_plugin_manager()
    cfg = PiConfigParser(str(tmpdir.join('pibooth.cfg')), pm)
    pm.load_all_plugins([], [])
    language.init(str(tmpdir.join('translations.cfg')))
    pm.hook.pibooth_configure(cfg=cfg)
    win = PiWindow("Test", (800, 480))
    menu = PiConfigMenu(pm, cfg, ApplicationMock(tmpdir, printer), win)
    menu.show()
    return menu


def button_titles(submenu):
    return [widget.get_title() for widget in submenu.get_widgets()
            if isinstance(widget, pgm.widgets.Button)]


def process(menu, events=()):
    menu.process(list(events) + list(pygame.event.get()))


def test_show(menu):
    assert menu.is_shown()
    for _ in range(3):
        process(menu)
    assert menu.is_shown()
    assert menu._main_menu.get_current() is menu._main_menu
    assert isinstance(menu._main_menu.get_selected_widget(), pgm.widgets.Button)


def test_enter_and_leave_submenu(menu):
    main = menu._main_menu
    process(menu)
    button = main.get_selected_widget()
    assert isinstance(button, pgm.widgets.Button)
    assert button.get_title() != 'Exit'

    process(menu, [menu.create_click_event()])
    submenu = main.get_current()
    assert submenu is not main
    assert submenu.get_title() == button.get_title()
    assert menu.is_shown()

    process(menu, [menu.create_next_event()])
    assert main.get_current() is submenu

    process(menu, [menu.create_back_event()])
    assert main.get_current() is main
    assert menu.is_shown()


def _key(key, unicode=''):
    """Build the event pygame reports for a physical key press."""
    return pygame.event.Event(pygame.KEYDOWN, key=key, unicode=unicode,
                              mod=0, scancode=41, window=None, test=True)


def select_in_submenu(menu, is_wanted):
    """Enter the first submenu holding a wanted widget, and select it."""
    main = menu._main_menu
    process(menu)
    for button in [w for w in main.get_widgets() if isinstance(w, pgm.widgets.Button)]:
        if button.get_title() == 'Exit':
            continue
        main.select_widget(button)
        process(menu, [menu.create_click_event()])
        wanted = [w for w in main.get_current().get_widgets() if is_wanted(w)]
        if wanted:
            main.get_current().select_widget(wanted[0])
            process(menu)
            return wanted[0]
        process(menu, [menu.create_back_event()])
    raise AssertionError("No such widget found in the menu")


def is_text_input(widget):
    return isinstance(widget, pgm.widgets.TextInput) and not isinstance(widget, pgm.widgets.ColorInput)


def test_close(menu):
    closed = []
    menu._close_callback = lambda: closed.append(True)
    process(menu)
    process(menu, [menu.create_back_event()])
    assert not menu.is_shown()
    assert closed == [True]


def test_escape_leaves_a_text_input(menu):
    """ESC is also the key deleting a character in the text inputs of
    pygame-menu: given to them, it ate a character instead of leaving the
    submenu.
    """
    text_input = select_in_submenu(menu, is_text_input)
    submenu = menu._main_menu.get_current()
    assert submenu is not menu._main_menu
    value = text_input.get_value()

    process(menu, [_key(pygame.K_ESCAPE, '\x1b')])

    assert text_input.get_value() == value, "ESC deleted a character"
    assert menu._main_menu.get_current() is menu._main_menu, "ESC did not leave the submenu"
    assert menu.is_shown()


def test_escape_leaves_a_color_input(menu):
    """A color input is a text input of pygame-menu, ESC used to be eaten
    by it as well.
    """
    color_input = select_in_submenu(menu, lambda w: isinstance(w, pgm.widgets.ColorInput))
    assert menu._main_menu.get_current() is not menu._main_menu
    value = color_input.get_value()

    process(menu, [_key(pygame.K_ESCAPE, '\x1b')])

    assert color_input.get_value() == value, "ESC changed the color"
    assert menu._main_menu.get_current() is menu._main_menu, "ESC did not leave the submenu"
    assert menu.is_shown()


def test_escape_closes_the_menu_from_a_submenu(menu):
    """Two ESC from a submenu: back to the main menu, then close.
    """
    closed = []
    menu._close_callback = lambda: closed.append(True)
    select_in_submenu(menu, is_text_input)

    process(menu, [_key(pygame.K_ESCAPE, '\x1b')])
    assert menu.is_shown()
    process(menu, [_key(pygame.K_ESCAPE, '\x1b')])

    assert not menu.is_shown()
    assert closed == [True]


def test_backspace_deletes_a_character(menu):
    """Remapping the 'back' key of pygame-menu on ESC also stole the
    backspace key of the text inputs.
    """
    text_input = select_in_submenu(menu, is_text_input)
    text_input.set_value('pibooth')
    process(menu)

    process(menu, [_key(pygame.K_BACKSPACE, '\x08')])

    assert text_input.get_value() == 'piboot'
    assert menu._main_menu.get_current() is not menu._main_menu, "Backspace left the submenu"


def test_printer_queue_entry(menu):
    assert "Printer queue" in button_titles(menu._build_submenu('PRINTER'))


def test_printer_queue_entry_hidden_without_printer(menu, monkeypatch):
    monkeypatch.setattr(printer_module, 'cups', None)
    menu.app.printer = Printer()
    assert "Printer queue" not in button_titles(menu._build_submenu('PRINTER'))


def test_printer_queue_cancel(menu, printer, fond_path):
    printer.print_file(fond_path)
    assert len(printer.get_all_tasks()) == 1

    submenu = menu._build_submenu_printer("Printer queue")
    label = submenu.get_widgets()[0]
    assert label.get_title().split()[-1] == '1'

    menu._on_printer_cancel(label)
    assert printer.get_all_tasks() == {}
    assert label.get_title().split()[-1] == '0'


def test_printer_queue_cancel_failure(menu, printer, fond_path):
    """A CUPS error shall be logged, not raised in the user face."""
    printer.print_file(fond_path)
    submenu = menu._build_submenu_printer("Printer queue")
    label = submenu.get_widgets()[0]

    def boom(name):
        raise RuntimeError("CUPS is gone")

    printer._conn.cancelAllJobs = boom
    menu._on_printer_cancel(label)  # Shall not raise
    assert len(printer.get_all_tasks()) == 1


def test_keyboard_is_built_on_demand(menu):
    """The virtual keyboard shall not be built when it is not used.
    """
    assert menu._keyboard is None
    for _ in range(3):
        process(menu)
    assert menu._keyboard is None


def test_menu_is_painted_inside_its_own_area(menu):
    """Only the area of the menu is copied back on the window.
    """
    surface = menu.win.surface
    surface.fill((17, 90, 140))
    before = surface.copy()

    process(menu)

    rect = menu.get_rect()
    assert pygame.image.tostring(surface.subsurface(rect), 'RGB') != \
        pygame.image.tostring(before.subsurface(rect), 'RGB'), "The menu was not painted"

    above = pygame.Rect(0, 0, surface.get_width(), rect.top)
    below = pygame.Rect(0, rect.bottom, surface.get_width(), surface.get_height() - rect.bottom)
    for outside in (above, below):
        if outside.height > 0:
            assert pygame.image.tostring(surface.subsurface(outside), 'RGB') == \
                pygame.image.tostring(before.subsurface(outside), 'RGB'), "Painted outside the menu"


def test_menu_surface_blends_like_pygame():
    """Both blitters shall give the same picture, up to a rounding unit.
    """
    source = pygame.Surface((20, 20), pygame.SRCALPHA, 32)
    source.fill((200, 100, 50, 128))

    reference = pygame.Surface((20, 20))
    reference.fill((10, 20, 30))
    reference.blit(source, (0, 0))  # Blended by pygame

    fast = _MenuSurface((20, 20))
    fast.fill((10, 20, 30))
    fast.blit(source, (0, 0))  # Blended by SDL

    for pos in ((0, 0), (10, 10), (19, 19)):
        for got, expected in zip(fast.get_at(pos), reference.get_at(pos)):
            assert abs(got - expected) <= 2, "{} != {}".format(fast.get_at(pos), reference.get_at(pos))


def test_menu_surface_has_the_format_of_the_window(menu):
    """A blit between two different pixel formats is much slower.
    """
    menu.process([])
    assert menu._surface.get_masks() == menu.win.surface.get_masks()
    assert menu._surface.get_bitsize() == menu.win.surface.get_bitsize()


def _finger(surface, pos, pressed=True):
    """Build the finger event SDL reports for a touch at the given position."""
    width, height = surface.get_size()
    return pygame.event.Event(pygame.FINGERDOWN if pressed else pygame.FINGERUP,
                              touch_id=6, finger_id=73, x=pos[0] / width, y=pos[1] / height,
                              dx=0.0, dy=0.0, pressure=0.0)


def _synthetic_mouse(pos, pressed=True):
    """Build the mouse event SDL synthesises on top of a touch."""
    return pygame.event.Event(pygame.MOUSEBUTTONDOWN if pressed else pygame.MOUSEBUTTONUP,
                              pos=pos, button=1, touch=True, window=None)


def test_a_touch_is_not_handled_twice(menu):
    """SDL reports a touch as a finger event and as a mouse event. Both are
    handled by the virtual keyboard, which used to insert the character twice.
    """
    menu.cfg.set('GENERAL', 'vkeyboard', 'True')
    surface = menu.win.surface
    main = menu._main_menu
    process(menu)

    # Reach a text input and open the virtual keyboard by touching it
    for button in [w for w in main.get_widgets() if isinstance(w, pgm.widgets.Button)]:
        main.select_widget(button)
        process(menu, [menu.create_click_event()])
        inputs = [w for w in main.get_current().get_widgets()
                  if isinstance(w, pgm.widgets.TextInput) and not isinstance(w, pgm.widgets.ColorInput)]
        if inputs:
            break
        process(menu, [menu.create_back_event()])
    assert inputs, "No text input found in the menu"

    text_input = inputs[0]
    main.get_current().select_widget(text_input)
    text_input.set_value('')
    process(menu)

    pos = text_input.get_rect(to_real_position=True).center
    process(menu, [_finger(surface, pos), _synthetic_mouse(pos)])
    assert menu._keyboard is not None and menu._keyboard.is_enabled()
    process(menu)

    key = menu._keyboard.layout.get_key('a')
    assert key is not None, "No 'a' key on the virtual keyboard"
    pos = key.rect.center
    process(menu, [_finger(surface, pos), _synthetic_mouse(pos)])

    assert menu._keyboard.input.text == 'a', \
        "One touch inserted {!r}".format(menu._keyboard.input.text)


def test_the_keyboard_survives_a_touch_in_a_window(menu):
    """SDL gives finger positions relative to the window. Converted with the
    size of the desktop, a touch on the virtual keyboard lands outside of it
    and closes it, as soon as the booth does not run fullscreen.
    """
    menu.cfg.set('GENERAL', 'vkeyboard', 'True')
    surface = menu.win.surface
    # A booth running in a window on a bigger desktop
    menu.win.display_size = (surface.get_width() * 2, surface.get_height() * 2)
    main = menu._main_menu
    process(menu)

    for button in [w for w in main.get_widgets() if isinstance(w, pgm.widgets.Button)]:
        main.select_widget(button)
        process(menu, [menu.create_click_event()])
        inputs = [w for w in main.get_current().get_widgets()
                  if isinstance(w, pgm.widgets.TextInput) and not isinstance(w, pgm.widgets.ColorInput)]
        if inputs:
            break
        process(menu, [menu.create_back_event()])
    assert inputs, "No text input found in the menu"

    main.get_current().select_widget(inputs[0])
    inputs[0].set_value('')
    process(menu)
    process(menu, [_finger(surface, inputs[0].get_rect(to_real_position=True).center)])
    assert menu._keyboard is not None and menu._keyboard.is_enabled()
    process(menu)

    key = menu._keyboard.layout.get_key('a')
    process(menu, [_finger(surface, key.rect.center)])

    assert menu._keyboard.is_enabled(), "Touching the keyboard closed it"
    assert menu._keyboard.input.text == 'a'
