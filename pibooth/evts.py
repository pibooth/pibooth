# -*- coding: utf-8 -*-

import pygame
from pygame._sdl2 import touch

# Events generated by hardware button and handled by the view
EVT_BUTTON_CAPTURE = pygame.USEREVENT + 201             # buttons, leds
EVT_BUTTON_PRINT = pygame.USEREVENT + 202               # buttons, leds
EVT_BUTTON_SETTINGS = pygame.USEREVENT + 203            # buttons, leds

# Events handled by the controller (app and plugins)
EVT_PIBOOTH_PRINTER_UPDATE = pygame.USEREVENT + 204     # notification
EVT_PIBOOTH_CAM_PREVIEW = pygame.USEREVENT + 205        # result
EVT_PIBOOTH_CAM_CAPTURE = pygame.USEREVENT + 206        # result
EVT_PIBOOTH_CAPTURE = pygame.USEREVENT + 207
EVT_PIBOOTH_PRINT = pygame.USEREVENT + 208
EVT_PIBOOTH_SETTINGS = pygame.USEREVENT + 209           # menu_shown


def post(*args, **kwargs):
    """Post an envent to be processed later by tha main loop. Usefull
    for thread safe action on view.

    The default implementation use the Pygame event mechanism.
    """
    return pygame.event.post(pygame.event.Event(*args, **kwargs))


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


def get_top_visible(sprites, from_layers=(1, 2, 3, 4, 5)):
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


def is_button_print_event(event):
    """Return True if capture button event.
    """
    return event.type == EVT_BUTTON_PRINT


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
            # Re-raise exception from async tasks
            if getattr(event, 'exception', None):
                raise event.exception
            return event
    return None
