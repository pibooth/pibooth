# -*- coding: utf-8 -*-

import pygame
from pibooth.booth import PiApplication


class ApplicationStub:

    """The part of the application needed to find the events. Building a real
    one requires a camera and the GPIO of a Raspberry Pi.
    """

    find_settings_event = PiApplication.find_settings_event

    def __init__(self):
        self._escape_held = False
        self._fingerdown_events = []
        self.buttons = None


def _escape():
    """Build the event pygame reports for a press on the escape key."""
    return pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE, unicode='\x1b',
                              mod=0, scancode=41, window=None)


def _hold_escape(monkeypatch, held):
    """Tell pygame whether the escape key is physically pressed."""
    keys = [False] * 512
    keys[pygame.K_ESCAPE] = held
    monkeypatch.setattr(pygame.key, 'get_pressed', lambda: keys)


def test_escape_opens_the_menu(monkeypatch):
    _hold_escape(monkeypatch, True)
    app = ApplicationStub()
    assert app.find_settings_event([_escape()]) is not None


def test_the_key_press_which_closed_the_menu_does_not_reopen_it(monkeypatch):
    """The menu enables the auto-repeat of the keyboard, and pygame does not
    cancel the repetition it has already scheduled when the menu restores the
    default on close: the repeated key press used to reopen the menu at once.
    """
    app = ApplicationStub()
    app._escape_held = True  # The menu has just been closed, ESC is still held

    _hold_escape(monkeypatch, True)
    assert app.find_settings_event([_escape()]) is None, "The menu was reopened"

    _hold_escape(monkeypatch, False)  # The key is released
    assert app.find_settings_event([]) is None
    assert not app._escape_held

    assert app.find_settings_event([_escape()]) is not None, "A new key press shall open the menu"


def test_the_key_release_is_awaited_to_open_the_menu_again(monkeypatch):
    """The escape key is ignored as long as it is not released, whatever the
    number of repetitions pygame sends in the meantime.
    """
    app = ApplicationStub()
    app._escape_held = True
    _hold_escape(monkeypatch, True)

    for _ in range(5):
        assert app.find_settings_event([_escape()]) is None
    assert app._escape_held
