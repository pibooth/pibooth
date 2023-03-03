# -*- coding: utf-8 -*-

import os
import pytest
import pygame
from pibooth.view.window import PiWindow


WIN = PiWindow("Test", debug=True)


def loop(func, *args, **kwargs):
    fps = 40
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                WIN.drop_cache()
                return
            if event.type == pygame.VIDEORESIZE:
                WIN.resize(event.size)

        func(*args, **kwargs)

        pygame.display.update()
        clock.tick(fps)

        if os.environ.get('SDL_VIDEODRIVER') == "dummy":
            # Automatic tests without video device available
            break


def test_oops(init):
    loop(WIN.show_oops)


def test_intro(init):
    loop(WIN.show_intro)


def test_intro_portrait(init, captures_portrait):
    loop(WIN.show_intro, captures_portrait[0])


def test_intro_landscape(init, captures_landscape):
    loop(WIN.show_intro, captures_landscape[0])


@pytest.mark.parametrize('choices', [(1, 2), (1, 3), (1, 4)])
def test_choice(init, choices):
    loop(WIN.show_choice, choices)


@pytest.mark.parametrize('selected', [1, 2, 3, 4])
def test_choice_selected(init, selected):
    loop(WIN.show_choice, (0, 0), selected)


def test_preview(init):
    loop(WIN.set_capture_number, 3, 5)


def test_work_in_progress(init):
    loop(WIN.show_work_in_progress)


def test_print(init):
    loop(WIN.show_print)


def test_print_portrait(init, captures_portrait):
    loop(WIN.show_print, captures_portrait[0])


def test_print_landscape(init, captures_landscape):
    loop(WIN.show_print, captures_landscape[0])


def test_finished(init):
    loop(WIN.show_finished)


def test_finished_portrait(init, captures_portrait):
    loop(WIN.show_finished, captures_portrait[0])


def test_finished_landscape(init, captures_landscape):
    loop(WIN.show_finished, captures_landscape[0])
