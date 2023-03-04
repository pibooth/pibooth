# -*- coding: utf-8 -*-

import pytest
import pygame


@pytest.mark.parametrize("name", ['wait', 'choose', 'chosen', 'preview', 'capture', 'processing', 'print', 'finish'])
def test_scene(init, pygame_loop, scene_builder, name):

    scene = scene_builder(name)

    def handler(screen, events):
        for event in events:
            if event.type == pygame.VIDEORESIZE:
                scene.set_background((0, 0, 0), event.size)
                scene.resize(event.size)

        scene.update(events)
        return scene.draw(screen)

    pygame_loop(handler)
