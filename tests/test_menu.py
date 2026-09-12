# -*- coding: utf-8 -*-

import pytest
import pygame
import pygame_menu as pgm
from pibooth import language
from pibooth.counters import Counters
from pibooth.plugins import create_plugin_manager
from pibooth.config.parser import PiConfigParser
from pibooth.config.menu import PiConfigMenu
from pibooth.view.window import PiWindow


class ApplicationMock:

    def __init__(self, tmpdir):
        self.count = Counters(str(tmpdir.join('counters.json')), taken=0, printed=0, forgotten=0)
        self.enabled = []
        self.disabled = []

    def enable_plugin(self, plugin):
        self.enabled.append(plugin)

    def disable_plugin(self, plugin):
        self.disabled.append(plugin)


@pytest.fixture
def menu(tmpdir):
    pm = create_plugin_manager()
    cfg = PiConfigParser(str(tmpdir.join('pibooth.cfg')), pm)
    pm.load_all_plugins([], [])
    language.init(str(tmpdir.join('translations.cfg')))
    pm.hook.pibooth_configure(cfg=cfg)
    win = PiWindow("Test", (800, 480))
    menu = PiConfigMenu(pm, cfg, ApplicationMock(tmpdir), win)
    menu.show()
    return menu


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
