# -*- coding: utf-8 -*-

import itertools
import pygame
from pibooth.pictures import text_to_pygame_image


POSITIONS = ["top-left",
             "top-center",
             "top-right",
             "center-left",
             "center",
             "center-right",
             "bottom-left",
             "bottom-center",
             "bottom-right"]

MULTILINES = ["This is a\ntop-left\ncool position",
              "This is a\ntop-center\ncool position",
              "This is a\ntop-right\ncool position",
              "This is a\ncenter-left\ncool position",
              "This is a\ncenter\ncool position",
              "This is a\ncenter-right\ncool position",
              "This is a\nbottom-left\ncool position",
              "This is a\nbottom-center\ncool position",
              "This is a\nbottom-right\ncool position"]


def test_text_position(pygame_loop):

    index = itertools.cycle(POSITIONS)

    def events_handler(screen, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                text = next(index)
                screen.fill((0, 0, 0))
                surface = text_to_pygame_image(text, screen.get_size(),
                                               color=(255, 255, 255),
                                               align=text,
                                               bg_color=(234, 23, 89))
                screen.blit(surface, (0, 0))
                return surface.get_rect()

    pygame_loop(events_handler)


def test_text_multilines(pygame_loop):

    index = itertools.cycle(MULTILINES)

    def events_handler(screen, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                text = next(index)
                screen.fill((0, 0, 0))
                surface = text_to_pygame_image(text, screen.get_size(),
                                               color=(255, 255, 255),
                                               align=POSITIONS[MULTILINES.index(text)],
                                               bg_color=(234, 23, 89))
                screen.blit(surface, (0, 0))
                return surface.get_rect()

    pygame_loop(events_handler)
