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


def test_close(menu):
    closed = []
    menu._close_callback = lambda: closed.append(True)
    process(menu)
    process(menu, [menu.create_back_event()])
    assert not menu.is_shown()
    assert closed == [True]


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
