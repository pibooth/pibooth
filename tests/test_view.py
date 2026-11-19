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


def test_refresh_display(init_pygame, monkeypatch):
    """The whole window is pushed when something changed, and during some frames
    after a full redraw (a part of a push may be lost with some drivers).
    """
    from pibooth.view.pygame.window import PygameWindow
    calls = []
    monkeypatch.setattr(pygame.display, 'update', lambda *args: calls.append(args))
    win = PygameWindow.__new__(PygameWindow)  # Only the refresh state is needed
    win._full_refresh_frames = 0

    assert not win.refresh_display([])  # Nothing changed
    assert win.refresh_display([pygame.Rect(0, 0, 10, 10)])
    assert calls == [()]  # Whole window, not the given rectangle

    calls.clear()
    assert win.refresh_display([pygame.Rect(0, 0, 800, 480)], forced=True, frames=3)
    assert win.refresh_display([])
    assert win.refresh_display([])
    assert not win.refresh_display([])  # Back to idle
    assert len(calls) == 3


@pytest.mark.parametrize("resolution", [(1934, 2464), (3280, 2464)])
def test_preview_frames_are_not_resized_again(init_lang, init_pygame, scene_builder, resolution):
    """A preview frame computed for the place given by the scene is displayed
    pixel for pixel (a second resize blurs and makes the details shimmer).
    """
    from pibooth.pictures import sizing
    scene = scene_builder('preview')
    rect = scene.get_image_rect()
    size = sizing.new_size_keep_aspect_ratio(resolution, rect.size)
    # One pixel checkerboard: any resampling would mix black and white pixels
    frame = Image.new('L', size)
    frame.putdata([255 * ((x + y) % 2) for y in range(size[1]) for x in range(size[0])])
    frame = frame.convert('RGB')
    scene.set_image(frame)

    drawn = scene.image.image
    area = pygame.Rect((0, 0), size)
    area.center = drawn.get_rect().center
    for x, y in [(0, 0), (1, 0), (size[0] // 2, size[1] // 2), (size[0] - 1, size[1] - 1)]:
        assert drawn.get_at((area.x + x, area.y + y))[:3] == frame.getpixel((x, y))


def test_camera_previews_at_the_displayed_size(cfg, pm, init_lang, init_pygame, scene_builder):
    """The camera is asked for frames at the size of the place where they are
    displayed, not at the size of the window minus a border.
    """
    from types import SimpleNamespace
    from pibooth.plugins.camera_plugin import CameraPlugin

    class FakeCamera:
        rect = None

        def preview(self, rect, flip=True):
            self.rect = rect

    scene = scene_builder('preview')
    win = SimpleNamespace(scene=scene, get_rect=lambda absolute=False: pygame.Rect(0, 0, 400, 400))
    app = SimpleNamespace(camera=FakeCamera())
    CameraPlugin(pm).state_preview_enter(cfg, app, win)
    assert app.camera.rect == scene.get_image_rect()

    # A scene without place for the image (no GUI) falls back to the window
    win.scene = SimpleNamespace(get_image_rect=lambda: None)
    CameraPlugin(pm).state_preview_enter(cfg, app, win)
    assert app.camera.rect == pygame.Rect(0, 0, 400, 400).inflate(-100, -100)


def test_choose_scene_tap_on_layout(init_lang, init_pygame, scene_builder):
    """Tapping the displayed layout chooses it, as the capture button (issue #647).
    """
    scene = scene_builder('choose')
    scene.set_choices((1, 4))
    scene.update([])
    scene.draw(init_pygame, True)
    slide = scene.slider.layout.get_visible_slides()[0]

    pygame.event.clear()
    scene.update([pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=slide.rect.center, button=1)])
    assert [event.type for event in pygame.event.get()] == [evts.EVT_PIBOOTH_CAPTURE]

    # A tap out of the layout, or with the mouse wheel, does nothing
    pygame.event.clear()
    scene.update([pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(1, 1), button=1),
                  pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=slide.rect.center, button=4)])
    assert evts.EVT_PIBOOTH_CAPTURE not in [event.type for event in pygame.event.get()]


def test_choose_scene_finger_on_layout(init_lang, init_pygame, scene_builder):
    scene = scene_builder('choose')
    scene.set_choices((1, 4))
    scene.update([])
    scene.draw(init_pygame, True)
    slide = scene.slider.layout.get_visible_slides()[0]
    width, height = pygame.display.get_surface().get_size()

    pygame.event.clear()
    scene.update([pygame.event.Event(pygame.FINGERDOWN, x=slide.rect.centerx / width,
                                     y=slide.rect.centery / height, touch_id=0, finger_id=0)])
    assert evts.EVT_PIBOOTH_CAPTURE in [event.type for event in pygame.event.get()]
