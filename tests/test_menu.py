# -*- coding: utf-8 -*-

import pytest
import pygame
import pygame_menu as pgm
from pibooth import language
from pibooth import printer as printer_module
from pibooth.counters import Counters
from pibooth.printer import Printer
from pibooth.plugins import create_plugin_manager
from pibooth.config.parser import PiboothConfigParser
from pibooth.view.pygame.menu import _MenuSurface
from pibooth.view.pygame.window import PygameWindow


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
def win(tmpdir, printer, init_pygame):
    pm = create_plugin_manager()
    cfg = PiboothConfigParser(str(tmpdir.join('pibooth.cfg')), pm)
    cfg.autostart_filename = str(tmpdir.join('autostart'))
    pm.load_all_plugins([], [])
    language.init(str(tmpdir.join('translations.cfg')))
    pm.hook.pibooth_configure(cfg=cfg)
    window = PygameWindow("Test", (800, 480))
    window.set_menu(ApplicationMock(tmpdir, printer), cfg, pm)
    window.toggle_menu()
    yield window
    window._menu.disable()


def process(win, events=()):
    win.update(list(events) + list(pygame.event.get()))
    win.draw()


def button_titles(submenu):
    return [widget.get_title() for widget in submenu.get_widgets()
            if isinstance(widget, pgm.widgets.Button)]


def test_show(win):
    assert win.is_menu_shown
    for _ in range(3):
        process(win)
    assert win.is_menu_shown
    assert win._menu.is_top_level()
    assert isinstance(win._menu._main_menu.get_selected_widget(), pgm.widgets.Button)


def test_enter_and_leave_submenu(win):
    main = win._menu._main_menu
    process(win)
    button = main.get_selected_widget()
    assert button.get_title() != 'Exit'

    win._menu.click()
    process(win)
    submenu = main.get_current()
    assert submenu is not main
    assert submenu.get_title() == button.get_title()
    assert win.is_menu_shown

    win._menu.next()
    process(win)
    assert main.get_current() is submenu

    win._menu.back()
    process(win)
    assert win._menu.is_top_level()
    assert win.is_menu_shown


def test_close(win):
    process(win)
    win.toggle_menu()
    assert not win.is_menu_shown
    assert not win._menu.is_enabled()


def test_printer_queue_entry(win):
    assert "Printer queue" in button_titles(win._menu._build_submenu('PRINTER'))


def test_printer_queue_entry_hidden_without_printer(win, monkeypatch):
    monkeypatch.setattr(printer_module, 'cups', None)
    win._menu.app.printer = Printer()
    assert "Printer queue" not in button_titles(win._menu._build_submenu('PRINTER'))


def test_printer_queue_cancel(win, printer, fond_path):
    printer.print_file(fond_path)
    assert len(printer.get_all_tasks()) == 1

    submenu = win._menu._build_submenu_printer("Printer queue")
    label = submenu.get_widgets()[0]
    assert label.get_title().split()[-1] == '1'

    win._menu.on_printer_cancel(label)
    assert printer.get_all_tasks() == {}
    assert label.get_title().split()[-1] == '0'


def test_printer_queue_cancel_failure(win, printer, fond_path):
    """A CUPS error shall be logged, not raised in the user face."""
    printer.print_file(fond_path)
    submenu = win._menu._build_submenu_printer("Printer queue")
    label = submenu.get_widgets()[0]

    def boom(name):
        raise RuntimeError("CUPS is gone")

    printer._conn.cancelAllJobs = boom
    win._menu.on_printer_cancel(label)  # Shall not raise
    assert len(printer.get_all_tasks()) == 1


def test_keyboard_is_built_on_demand(win):
    assert win._keyboard is None
    for _ in range(3):
        process(win)
    assert win._keyboard is None


def test_menu_is_painted_inside_its_own_area(win):
    surface = win.surface
    surface.fill((17, 90, 140))
    before = surface.copy()

    process(win)

    rect = win._menu.get_rect(surface)
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
            assert abs(got - expected) <= 2, f"{fast.get_at(pos)} != {reference.get_at(pos)}"


def test_menu_surface_has_the_format_of_the_window(win):
    """A blit between two different pixel formats is much slower.
    """
    process(win)
    assert win._menu._surface.get_masks() == win.surface.get_masks()
    assert win._menu._surface.get_bitsize() == win.surface.get_bitsize()


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


def _open_keyboard_on_a_text_input(win):
    """Reach a text input of the menu and open the virtual keyboard on it."""
    main = win._menu._main_menu
    process(win)
    for button in [w for w in main.get_widgets() if isinstance(w, pgm.widgets.Button)]:
        main.select_widget(button)
        win._menu.click()
        process(win)
        inputs = [w for w in main.get_current().get_widgets()
                  if isinstance(w, pgm.widgets.TextInput) and not isinstance(w, pgm.widgets.ColorInput)]
        if inputs:
            break
        win._menu.back()
        process(win)
    assert inputs, "No text input found in the menu"

    text_input = inputs[0]
    main.get_current().select_widget(text_input)
    text_input.set_value('')
    process(win)
    return text_input


def test_a_touch_is_not_handled_twice(win):
    """SDL reports a touch as a finger event and as a mouse event. Both are
    handled by the virtual keyboard, which used to insert the character twice.
    """
    win._menu.cfg.set('GENERAL', 'vkeyboard', 'True')
    surface = win.surface
    text_input = _open_keyboard_on_a_text_input(win)

    pos = text_input.get_rect(to_real_position=True).center
    process(win, [_finger(surface, pos), _synthetic_mouse(pos)])
    process(win)
    assert win._keyboard is not None and win._keyboard.is_enabled()

    key = win._keyboard.layout.get_key('a')
    assert key is not None, "No 'a' key on the virtual keyboard"
    pos = key.rect.center
    process(win, [_finger(surface, pos), _synthetic_mouse(pos)])

    assert win._keyboard.input.text == 'a', \
        f"One touch inserted {win._keyboard.input.text!r}"


def test_the_keyboard_survives_a_touch_in_a_window(win):
    """SDL gives finger positions relative to the window. Converted with the
    size of the desktop, a touch on the virtual keyboard lands outside of it
    and closes it, as soon as the booth does not run fullscreen.
    """
    win._menu.cfg.set('GENERAL', 'vkeyboard', 'True')
    surface = win.surface
    # A booth running in a window on a bigger desktop
    win.display_size = (surface.get_width() * 2, surface.get_height() * 2)
    text_input = _open_keyboard_on_a_text_input(win)

    process(win, [_finger(surface, text_input.get_rect(to_real_position=True).center)])
    process(win)
    assert win._keyboard is not None and win._keyboard.is_enabled()

    key = win._keyboard.layout.get_key('a')
    process(win, [_finger(surface, key.rect.center)])

    assert win._keyboard.is_enabled(), "Touching the keyboard closed it"
    assert win._keyboard.input.text == 'a'


def _key(key, unicode=''):
    """Build the event pygame reports for a physical key press."""
    return pygame.event.Event(pygame.KEYDOWN, key=key, unicode=unicode,
                              mod=0, scancode=41, window=None, test=True)


def select_in_submenu(win, is_wanted):
    """Enter the first submenu holding a wanted widget, and select it."""
    main = win._menu._main_menu
    process(win)
    for button in [w for w in main.get_widgets() if isinstance(w, pgm.widgets.Button)]:
        if button.get_title() == 'Exit':
            continue
        main.select_widget(button)
        win._menu.click()
        process(win)
        wanted = [w for w in main.get_current().get_widgets() if is_wanted(w)]
        if wanted:
            main.get_current().select_widget(wanted[0])
            process(win)
            return wanted[0]
        win._menu.back()
        process(win)
    raise AssertionError("No such widget found in the menu")


def is_text_input(widget):
    return isinstance(widget, pgm.widgets.TextInput) and not isinstance(widget, pgm.widgets.ColorInput)


def test_escape_leaves_a_text_input(win):
    """ESC is also the key deleting a character in the text inputs of
    pygame-menu: given to them, it ate a character instead of leaving the
    submenu.
    """
    text_input = select_in_submenu(win, is_text_input)
    assert not win._menu.is_top_level()
    value = text_input.get_value()

    process(win, [_key(pygame.K_ESCAPE, '\x1b')])

    assert text_input.get_value() == value, "ESC deleted a character"
    assert win._menu.is_top_level(), "ESC did not leave the submenu"
    assert win.is_menu_shown


def test_escape_leaves_a_color_input(win):
    """A color input is a text input of pygame-menu, ESC used to be eaten
    by it as well.
    """
    color_input = select_in_submenu(win, lambda w: isinstance(w, pgm.widgets.ColorInput))
    assert not win._menu.is_top_level()
    value = color_input.get_value()

    process(win, [_key(pygame.K_ESCAPE, '\x1b')])

    assert color_input.get_value() == value, "ESC changed the color"
    assert win._menu.is_top_level(), "ESC did not leave the submenu"
    assert win.is_menu_shown


def test_escape_closes_the_menu_from_a_submenu(win):
    """Two ESC from a submenu: back to the main menu, then close.
    """
    select_in_submenu(win, is_text_input)

    process(win, [_key(pygame.K_ESCAPE, '\x1b')])
    assert win.is_menu_shown
    process(win, [_key(pygame.K_ESCAPE, '\x1b')])

    assert not win.is_menu_shown


def test_backspace_deletes_a_character(win):
    """Remapping the 'back' key of pygame-menu on ESC also stole the
    backspace key of the text inputs.
    """
    text_input = select_in_submenu(win, is_text_input)
    text_input.set_value('pibooth')
    process(win)

    process(win, [_key(pygame.K_BACKSPACE, '\x08')])

    assert text_input.get_value() == 'piboot'
    assert not win._menu.is_top_level(), "Backspace left the submenu"


def _hold_escape(monkeypatch, held):
    """Tell pygame whether the escape key is physically pressed."""
    keys = [False] * 512
    keys[pygame.K_ESCAPE] = held
    monkeypatch.setattr(pygame.key, 'get_pressed', lambda: keys)


def test_the_key_press_which_closed_the_menu_does_not_reopen_it(win, monkeypatch):
    """The menu enables the auto-repeat of the keyboard, and pygame does not
    cancel the repetition it has already scheduled when the menu restores the
    default on close: the repeated key press used to reopen the menu at once.
    """
    process(win)
    _hold_escape(monkeypatch, True)  # ESC is held down

    process(win, [_key(pygame.K_ESCAPE, '\x1b')])
    assert not win.is_menu_shown, "ESC did not close the menu"

    # pygame keeps sending the repetitions of the key still held down
    for _ in range(3):
        process(win, [_key(pygame.K_ESCAPE, '\x1b')])
        assert not win.is_menu_shown, "The menu was reopened"

    _hold_escape(monkeypatch, False)  # The key is released
    process(win)
    process(win, [_key(pygame.K_ESCAPE, '\x1b')])
    process(win)  # EVT_BUTTON_SETTINGS is posted, it opens the menu at the next loop
    assert win.is_menu_shown, "A new key press shall open the menu"
