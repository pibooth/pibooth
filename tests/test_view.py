# -*- coding: utf-8 -*-

from types import SimpleNamespace
import pytest
import pygame
from pibooth import evts
from pibooth.view.pygame.window import PygameWindow


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
    """Both texts of the print scene are clickable (issue #463), the picture
    is a print action.
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


def test_settings_menu(init_lang, init_pygame, cfg, pm, counters):
    """Build the settings menu, enter a sub-menu and come back.
    """
    win = PygameWindow("Test", size=(400, 400))
    win.set_menu(SimpleNamespace(count=counters), cfg, pm)
    assert not win.is_menu_shown

    win.toggle_menu()
    assert win.is_menu_shown
    assert win._menu.is_enabled()
    assert win._menu.is_top_level()
    assert evts.EVT_PIBOOTH_SETTINGS in [event.type for event in pygame.event.get()]

    # Enter the first sub-menu (first selected widget is the 'General' button)
    win._menu.click()
    win.update(pygame.event.get())
    win.draw()
    assert not win._menu.is_top_level()
    assert win._menu._main_menu.get_current().get_title() == 'General'

    # Go back to the main menu
    win._menu.back()
    win.update(pygame.event.get())
    win.draw()
    assert win._menu.is_top_level()

    win.toggle_menu()
    assert not win.is_menu_shown
    assert not win._menu.is_enabled()
