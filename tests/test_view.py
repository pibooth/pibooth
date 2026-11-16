# -*- coding: utf-8 -*-

import pytest
import pygame
from PIL import Image
from pibooth import evts


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


def _press(scene, sprite):
    """Simulate a click on the given sprite and return the posted events.
    """
    pygame.event.clear()
    scene.update([pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=sprite.rect.center, button=1)])
    scene.update([pygame.event.Event(pygame.MOUSEBUTTONUP, pos=sprite.rect.center, button=1)])
    return [event.type for event in pygame.event.get()]


def test_print_scene_actions(init_lang, init_pygame, scene_builder):
    """Both texts of the print scene are clickable (issue #463).
    """
    scene = scene_builder('print')

    assert _press(scene, scene.text_print) == [evts.EVT_PIBOOTH_PRINT]
    assert _press(scene, scene.right_arrow) == [evts.EVT_PIBOOTH_PRINT]
    assert _press(scene, scene.text_forget) == [evts.EVT_PIBOOTH_CAPTURE]
    assert _press(scene, scene.left_arrow) == [evts.EVT_PIBOOTH_CAPTURE]

    # The picture is not part of the sprites group, press it directly
    pygame.event.clear()
    scene.image.set_pressed(1)
    scene.image.set_pressed(0)
    assert [event.type for event in pygame.event.get()] == [evts.EVT_PIBOOTH_PRINT]


def test_capture_scene_flash(init_lang, init_pygame, scene_builder):
    """Only the background is lit during the capture, the last preview frame
    stays displayed.
    """
    screen = init_pygame
    scene = scene_builder('capture')
    scene.set_image(Image.new('RGB', (200, 200), (255, 0, 0)))
    scene.update([])
    scene.draw(screen, True)
    # A point of the background out of any sprite (and of the outlines)
    corner, center = (20, 20), scene.image.rect.center
    assert screen.get_at(corner)[:3] == (0, 0, 0)
    assert screen.get_at(center)[:3] == (255, 0, 0)

    scene.set_flash(True)
    scene.set_flash(True)  # Lit once, whatever the number of calls
    for _ in range(3):  # The flash is steady, it does not blink
        scene.update([])
        scene.draw(screen)
        assert screen.get_at(corner)[:3] == (255, 255, 255)
        assert screen.get_at(center)[:3] == (255, 0, 0)

    scene.set_flash(False)
    scene.update([])
    scene.draw(screen)
    assert screen.get_at(corner)[:3] == (0, 0, 0)
    assert screen.get_at(center)[:3] == (255, 0, 0)


def test_capture_scene_no_flash(init_lang, init_pygame, scene_builder):
    screen = init_pygame
    scene = scene_builder('capture')
    scene.set_flash(False)
    for _ in range(3):
        scene.update([])
        scene.draw(screen, True)
        assert screen.get_at((20, 20))[:3] == (0, 0, 0)


def test_capture_scene_flash_over_a_scene_change(init_lang, init_pygame, scene_builder):
    """The window puts the background back when the scene is left during a flash
    (the background sprite is shared): the next flash shall work the same.
    """
    scene = scene_builder('capture')
    scene.set_flash(True)
    scene.background.set_skin((0, 0, 0))  # As 'PygameWindow.set_scene()' does
    scene.set_flash(True)
    assert scene.background.get_skin() == (255, 255, 255)
    scene.set_flash(False)
    assert scene.background.get_skin() == (0, 0, 0)
