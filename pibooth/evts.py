# -*- coding: utf-8 -*-

import pygame
from pygame._sdl2 import touch
import pygame_menu as pgm

EVT_PIBOOTH_BTN_CAPTURE = pygame.USEREVENT + 201
EVT_PIBOOTH_BTN_PRINT = pygame.USEREVENT + 202
EVT_PIBOOTH_BTN_SETTINGS = pygame.USEREVENT + 203
EVT_PIBOOTH_PRINTER_UPDATE = pygame.USEREVENT + 204
EVT_PIBOOTH_CAM_PREVIEW = pygame.USEREVENT + 205
EVT_PIBOOTH_CAM_CAPTURE = pygame.USEREVENT + 206


_EVT_EMITTER = pygame.event.post


def post(*args, **kwargs):
    """Post an envent to be processed later by tha main loop. Usefull
    for thread safe action on view.

    The default implementation use the Pygame event mechanism.
    """
    return _EVT_EMITTER(pygame.event.Event(*args, **kwargs))


def post_capture_button_event():
    """Post EVT_PIBOOTH_BTN_CAPTURE.
    """
    return post(EVT_PIBOOTH_BTN_CAPTURE)


def post_print_button_event():
    """Post EVT_PIBOOTH_BTN_PRINT.
    """
    return post(EVT_PIBOOTH_BTN_PRINT)


def post_settings_button_event():
    """Post EVT_PIBOOTH_BTN_SETTINGS.
    """
    return post(EVT_PIBOOTH_BTN_SETTINGS)


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


def get_top_visible(sprites, from_layers=(1, 2, 3, 4)):
    """Return the top sprite (last of the list) which is visible.

    :param sprites: sprites list
    :type sprites: list
    :param from_layers: layers to belong to
    :type from_layers: list
    """
    for sp in reversed(sprites):
        if sp.visible and sp.layer in from_layers:
            return sp
    return None


def is_fullscreen_event(event):
    """Return True if fullscreen event.
    """
    return event.type == pygame.KEYDOWN and \
        event.key == pygame.K_f and pygame.key.get_mods() & pygame.KMOD_CTRL


def is_fingers_event(event, nbr_fingers):
    """Return True if screen is touched with the number of fingers (or more).
    """
    return event.type == pygame.FINGERDOWN and touch.get_num_fingers(event.touch_id) >= nbr_fingers


def is_button_settings_event(event):
    """Return True if settings event.
    """
    return event.type == EVT_PIBOOTH_BTN_SETTINGS


def is_button_capture_event(event):
    """Return True if capture button event.
    """
    return event.type == EVT_PIBOOTH_BTN_CAPTURE


def is_button_print_event(event):
    """Return True if capture button event.
    """
    return event.type == EVT_PIBOOTH_BTN_PRINT


def is_printer_status_event(event):
    """Return True if printer status event.
    """
    return event.type == EVT_PIBOOTH_PRINTER_UPDATE


def is_camera_capture_event(event):
    """Return True if camera capture event.
    """
    return event.type == EVT_PIBOOTH_CAM_CAPTURE


def is_camera_preview_event(event):
    """Return True if camera preview event.
    """
    return event.type == EVT_PIBOOTH_CAM_PREVIEW


def find_event(events, event_type):
    """Return the first found event if found in the list.
    """
    for event in events:
        if event.type == event_type:
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
