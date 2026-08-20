"""Plugin to display 'Get Ready' at screen after 'wait' state."""

import time
import pygame
import pibooth
from pibooth import pictures, fonts

__version__ = "0.0.2"


class GetReadyPlugin(object):
    name = 'pibooth-core:getReady'

    def __init__(self, plugin_manager):
        self._pm = plugin_manager
        self.blink_time = 0.3

    @pibooth.hookimpl
    def state_wait_exit(self, cfg, app, win):
        if cfg.getfloat('WINDOW', 'get_ready_delay') == 0: return

        win_rect = win.get_rect()
        text = "Get Ready!"

        # Get best font size according to window size
        font = fonts.get_pygame_font(text, fonts.CURRENT,
                                     win_rect.width//1.5, win_rect.height//1.5)

        # Build a surface to display at screen
        text_surface = font.render(text, True, win.text_color)

        # Clear screen
        if isinstance(win.bg_color, (tuple, list)):
            win.surface.fill(win.bg_color)
        else:
            bg_surface = pictures.get_pygame_image(win.bg_color, win_rect.size, crop=True, color=None)
            win.surface.blit(bg_surface, (0, 0))

        # Draw the surface at screen
        win.surface.blit(text_surface, text_surface.get_rect(center=win_rect.center).topleft)

        # Force screen update and events process
        pygame.display.update()
        pygame.event.pump()

        time.sleep(cfg.getfloat('WINDOW', 'get_ready_delay'))
