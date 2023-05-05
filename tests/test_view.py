# -*- coding: utf-8 -*-

import pytest
import pygame


@pytest.mark.parametrize("name", ['wait', 'choose', 'chosen', 'preview', 'capture', 'processing', 'print', 'finish'])
def test_scene(init_lang, pygame_loop, scene_builder, name):

    scene = scene_builder(name)

    def events_handler(screen, events):
        for event in events:
            if event.type == pygame.VIDEORESIZE:
                scene.resize(event.size)

        scene.update(events)
        return scene.draw(screen)

    pygame_loop(events_handler)


def test_get_sprites(init_lang, scene_builder):

    scene = scene_builder('wait')
    assert scene.status_bar.get_sprites()
