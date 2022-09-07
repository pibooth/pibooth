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


if __name__ == '__main__':
    pygame.init()
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((400, 400))
    screen.fill((0, 0, 0))

    run = True
    index_right = itertools.cycle(POSITIONS)
    index_left = itertools.cycle(MULTILINES)

    while run:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_RIGHT:
                    text = next(index_right)
                    screen.fill((0, 0, 0))
                    surface = text_to_pygame_image(text, screen.get_size(),
                                                   color=(255, 255, 255),
                                                   align=text,
                                                   bg_color=(234, 23, 89))
                    screen.blit(surface, (0, 0))

                if event.key == pygame.K_LEFT:
                    text = next(index_left)
                    screen.fill((0, 0, 0))
                    surface = text_to_pygame_image(text, screen.get_size(),
                                                   color=(255, 255, 255),
                                                   align=POSITIONS[MULTILINES.index(text)],
                                                   bg_color=(234, 23, 89))
                    screen.blit(surface, (0, 0))

        pygame.display.flip()

        clock.tick(5)
