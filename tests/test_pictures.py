# -*- coding: utf-8 -*-

import itertools
import pytest
import pygame
from pibooth import pictures
from pibooth.pictures import sizing

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


def test_resize_original_small_inner():
    size = sizing.new_size_keep_aspect_ratio((600, 200), (900, 600))
    assert size == (900, 300)


def test_resize_original_small_outer():
    size = sizing.new_size_keep_aspect_ratio((600, 200), (900, 600), 'outer')
    assert size == (1800, 600)


def test_resize_original_big_inner():
    size = sizing.new_size_keep_aspect_ratio((1000, 1200), (800, 600))
    assert size == (500, 600)


def test_resize_original_big_outer():
    size = sizing.new_size_keep_aspect_ratio((1000, 1200), (800, 600), 'outer')
    assert size == (800, 960)


def test_crop_original_small_left():
    coordinates = sizing.new_size_by_croping((600, 200), (900, 600), 'top-left')
    assert coordinates == (0, 0, 900, 600)


def test_crop_original_small_middle():
    coordinates = sizing.new_size_by_croping((600, 200), (900, 600))
    assert coordinates == (-150, -200, 750, 400)


def test_crop_original_big_topleft():
    coordinates = sizing.new_size_by_croping((1000, 1200), (800, 600), 'top-left')
    assert coordinates == (0, 0, 800, 600)


def test_crop_original_big_middle():
    coordinates = sizing.new_size_by_croping((1000, 1200), (800, 600))
    assert coordinates == (100, 300, 900, 900)


def test_crop_ratio_original_small_left():
    coordinates = sizing.new_size_by_croping_ratio((600, 200), (900, 600), 'top-left')
    assert coordinates == (0, 0, 300, 200)


def test_crop_ratio_original_small_middle():
    coordinates = sizing.new_size_by_croping_ratio((600, 200), (900, 600))
    assert coordinates == (150, 0, 450, 200)


def test_crop_ratio_original_big_topleft():
    coordinates = sizing.new_size_by_croping_ratio((1000, 1200), (800, 600), 'top-left')
    assert coordinates == (0, 0, 1000, 750)


def test_crop_ratio_original_big_middle():
    coordinates = sizing.new_size_by_croping_ratio((1000, 1200), (800, 600))
    assert coordinates == (0, 225, 1000, 975)


def test_colorize_pil_image(captures_portrait):
    assert pictures.colorize_pil_image(captures_portrait[0], (255, 0, 0))


def test_colorize_pygame_image(init_pygame):
    surface = pictures.load_pygame_image('dot.png')
    assert pygame.transform.average_color(surface)[:3] == (255, 255, 255)
    surface = pictures.colorize_pygame_image(surface, (255, 0, 0))
    assert pygame.transform.average_color(surface)[:3] == (255, 0, 0)


def test_load_pygame_image(init_pygame, fond_path):
    with pytest.raises(ValueError):
        pictures.load_pygame_image('toto.png')

    assert pictures.load_pygame_image(fond_path)


def test_transform_pygame_image(init_pygame):
    surface = pictures.load_pygame_image('dot.png')
    assert pictures.transform_pygame_image(surface, (64, 64), antialiasing=True, hflip=True, vflip=True,
                                           angle=45, crop=True, color=(255, 0, 0))


def test_text_position(pygame_loop):

    index = itertools.cycle(POSITIONS)

    def events_handler(screen, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                text = next(index)
                screen.fill((0, 0, 0))
                surface = pictures.text_to_pygame_image(text, screen.get_size(),
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
                surface = pictures.text_to_pygame_image(text, screen.get_size(),
                                                        color=(255, 255, 255),
                                                        align=POSITIONS[MULTILINES.index(text)],
                                                        bg_color=(234, 23, 89))
                screen.blit(surface, (0, 0))
                return surface.get_rect()

    pygame_loop(events_handler)


@pytest.mark.parametrize("index", [1, 2, 3, 4, 5])
def test_get_layout_asset(init_lang, init_pygame, index):
    if index > 4:
        with pytest.raises(ValueError):
            pictures.get_layout_asset(index, (255, 255, 255), (255, 0, 0))
    else:
        assert pictures.get_layout_asset(index, (255, 255, 255), (255, 0, 0))


def test_get_best_orientation_portrait(captures_portrait):
    assert pictures.get_best_orientation(captures_portrait[:1]) == pictures.PORTRAIT
    assert pictures.get_best_orientation(captures_portrait[:2]) == pictures.LANDSCAPE
    assert pictures.get_best_orientation(captures_portrait[:3]) == pictures.LANDSCAPE
    assert pictures.get_best_orientation(captures_portrait[:4]) == pictures.PORTRAIT


def test_get_best_orientation_landscape(captures_landscape):
    assert pictures.get_best_orientation(captures_landscape[:1]) == pictures.LANDSCAPE
    assert pictures.get_best_orientation(captures_landscape[:2]) == pictures.PORTRAIT
    assert pictures.get_best_orientation(captures_landscape[:3]) == pictures.PORTRAIT
    assert pictures.get_best_orientation(captures_landscape[:4]) == pictures.LANDSCAPE
