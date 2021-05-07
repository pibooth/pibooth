# -*- coding: utf-8 -*-

import pygame
from pibooth.view.window import PtbWindow


WIN = PtbWindow("Test", debug=True)


def loop(func, *args, **kwargs):
    fps = 40
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.VIDEORESIZE:
                WIN.resize(event.size)

        func(*args, **kwargs)

        pygame.display.update()
        clock.tick(fps)


def test_preview(init):
    loop(WIN.set_capture_number, 3, 5)


def test_finished(init):
    loop(WIN.show_finished)


def test_finished_portrait(init, captures_portrait):
    loop(WIN.show_finished, captures_portrait[0])


def test_finished_landscape(init, captures_landscape):
    loop(WIN.show_finished, captures_landscape[0])
