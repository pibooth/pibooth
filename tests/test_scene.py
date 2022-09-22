# -*- coding: utf-8 -*-

import pygame


def test_scene(init, pygame_loop, scene_builder):

    scene = scene_builder('preview')

    def handler(screen, events):
        for event in events:
            if event.type == pygame.VIDEORESIZE:
                scene.set_background((0, 0, 0), event.size)
                scene.resize(event.size)

        scene.update(events)
        return scene.draw(screen)

    pygame_loop(handler)
