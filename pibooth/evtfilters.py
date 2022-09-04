# -*- coding: utf-8 -*-

import pygame
from pygame._sdl2 import touch
import pygame_menu as pgm

EVT_BUTTONDOWN = pygame.USEREVENT + 1
EVT_PRINTER_TASKS_UPDATED = pygame.USEREVENT + 2
EVT_CAMERA_PREVIEW = pygame.USEREVENT + 3
EVT_CAMERA_CAPTURE = pygame.USEREVENT + 4


_EVT_EMITTER = pygame.event.post


def post(*args, **kwargs):
    """Post an envent to be processed later by tha main loop. Usefull
    for thread safe action on view.

    The default implementation use the Pygame event mechanism.
    """
    return _EVT_EMITTER(*args, **kwargs)


def get_event_pos(display_size, event):
    """
    Return the position from finger or mouse event on x-axis and y-axis (x, y).

    :param display_size: size of display for relative positioning in finger events
    :param event: pygame event object

    :return: position (x, y) in px
    :rtype: tuple
    """
    if event.type in (pygame.FINGERDOWN, pygame.FINGERMOTION, pygame.FINGERUP):
        finger_pos = (event.x * display_size[0], event.y * display_size[1])
        return finger_pos
    return event.pos


def is_quit_event(event):
    """Return True if quit event."""
    return event.type == pygame.QUIT


def is_resize_event(event):
    """Return True if resize event."""
    return event.type == pygame.VIDEORESIZE


def is_fullscreen_event(event):
    """Return True if fullscreen event:
        - CTRL + F key
    """
    return event.type == pygame.KEYDOWN and \
        event.key == pygame.K_f and pygame.key.get_mods() & pygame.KMOD_CTRL


def is_settings_event(event):
    """Return True if settings event:
        - ESCAPE key
        - CAPTURE button
        - 4 FINGERS touch
    """
    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
        return True
    if event.type == EVT_BUTTONDOWN and event.capture and event.printer:
        return True
    if event.type == pygame.FINGERDOWN:
        return touch.get_num_fingers(event.touch_id) > 3
    return False


def is_capture_button_event(event, window):
    """Return True if capture button event:
        - LEFT key
        - CAPTURE button
        - MOUSE click on half-left screen
        - FINGER touch on half-left screen
    """
    if event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
        return True
    if (event.type == pygame.MOUSEBUTTONUP and event.button in (1, 2, 3)) or event.type == pygame.FINGERUP:
        pos = get_event_pos(window.display_size, event)
        rect = window.get_rect()
        if pygame.Rect(0, 0, rect.width // 2, rect.height).collidepoint(pos):
            return True
    if event.type == EVT_BUTTONDOWN and event.capture:
        return True
    return False


def is_print_button_event(event, window):
    """Return True if capture button event:
        - RIGHT key
        - PRINTER button
        - MOUSE click on half-right screen
        - FINGER touch on half-right screen
    """
    if event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
        return True
    if (event.type == pygame.MOUSEBUTTONUP and event.button in (1, 2, 3)) or event.type == pygame.FINGERUP:
        pos = get_event_pos(window.display_size, event)
        rect = window.get_rect()
        if pygame.Rect(rect.width // 2, 0, rect.width // 2, rect.height).collidepoint(pos):
            return True
    if event.type == EVT_BUTTONDOWN and event.printer:
        return True
    return False


def is_printer_status_event(event):
    """Return True if printer status event."""
    return event.type == EVT_PRINTER_TASKS_UPDATED


def find_quit_event(events):
    """Return the first found event if found in the list.
    """
    for event in events:
        if is_quit_event(event):
            return event
    return None


def find_settings_event(events):
    """Return the first found event if found in the list.
    """
    for event in events:
        if is_settings_event(event):
            return event
    return None


def find_capture_event(events, window):
    """Return the first found event if found in the list.
    """
    for event in events:
        if is_capture_button_event(event, window):
            return event
    return None


def find_print_event(events, window):
    """Return the first found event if found in the list.
    """
    for event in events:
        if is_print_button_event(event, window):
            return event
    return None


def find_choice_event(events, window):
    """Return the first found event if found in the list.
    """
    for event in events:
        if is_capture_button_event(event, window):
            event.key = pygame.K_LEFT
            return event
        if is_print_button_event(event, window):
            event.key = pygame.K_RIGHT
            return event
    return None


def find_print_status_event(events):
    """Return the first found event if found in the list.
    """
    for event in events:
        if is_printer_status_event(event):
            return event
    return None


def create_click_event(button=True):
    """Create a pygame event to click on the currently selected
    widget on the menu. If the widget is a button, ENTER event
    is created, else LEFT event is created.
    """
    if button:
        event = pygame.event.Event(pygame.KEYDOWN, key=pgm.controls.KEY_APPLY,
                                   unicode='\r', mod=0, scancode=36,
                                   window=None, test=True)
    else:
        event = pygame.event.Event(pygame.KEYDOWN, key=pgm.controls.KEY_RIGHT,
                                   unicode=u'\uf703', mod=0, scancode=124,
                                   window=None, test=True)
    return event


def create_next_event():
    """Create a pygame event to select the next widget.
    """
    return pygame.event.Event(pygame.KEYDOWN, key=pgm.controls.KEY_MOVE_UP,
                              unicode=u'\uf701', mod=0, scancode=125,
                              window=None, test=True)


def create_back_event():
    """Create a pygame event to back to the previous menu.
    """
    return pygame.event.Event(pygame.KEYDOWN, key=pgm.controls.KEY_BACK,
                              unicode=u'\x1b', mod=0, scancode=53,
                              window=None, test=True)
