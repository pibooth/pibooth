# -*- coding: utf-8 -*-

import io
import time
import pygame
from PIL import Image, ImageDraw
import random
from pibooth.language import get_translated_text
from pibooth.camera.base import BaseCamera
from pibooth import fonts
from pibooth.utils import PoolingTimer, LOGGER

class FakeCamera(BaseCamera):
    def __init__(self, camera_proxy=None):
        self.not_found_text = get_translated_text('camera_not_found')
        LOGGER.info("New fake camera instance")
        super().__init__(camera_proxy)

    def _generate_still_image(self):
        size = self.resolution
        W, H = size
        font = fonts.get_pil_font(self.not_found_text, fonts.CURRENT, 0.5 * size[0], 0.5 * size[1])
        fake_camera = Image.new('RGB', size, 'red')
        textimg = ImageDraw.Draw(fake_camera)
        _, _, w, h = textimg.textbbox((0, 0), self.not_found_text, font=font)
        textimg.text(((W-w)/2, (H-h)/2), self.not_found_text, 'black', font)

        if self._overlay:
            fake_camera.paste(self._overlay, (0, 0), self._overlay)

        return fake_camera

    def _show_overlay(self, text, alpha):
        """Add an image as an overlay.
        """
        if self._window:  # No window means no preview displayed
            self._overlay = self.build_overlay(self.resolution, str(text), alpha)

    def preview(self, window, flip=True):
        """Setup the preview.
        """
        self._window = window
        self._build_and_display_preview()

    def _build_and_display_preview(self):
        rect = self.get_rect()
        still = self._generate_still_image()
        preview =  still.resize(rect.size)
        return self._window.show_image(preview)

    def preview_wait(self, timeout, alpha=80):
        """Wait the given time.
        """
        time.sleep(timeout)
        self._show_overlay(get_translated_text('smile'), alpha)

    def preview_countdown(self, timeout, alpha=80):
        """Show a countdown of `timeout` seconds on the preview.
        Returns when the countdown is finished.
        """
        timeout = int(timeout)
        if timeout < 1:
            raise ValueError("Start time shall be greater than 0")

        first_loop = True
        updated_rect = None
        timer = PoolingTimer(timeout)
        while not timer.is_timeout():
            remaining = int(timer.remaining() + 1)
            if not self._overlay or remaining != timeout:
                # Rebluid overlay only if remaining number has changed
                self._show_overlay(str(remaining), alpha)
                timeout = remaining
                updated_rect = self._build_and_display_preview()

            if first_loop:
                timer.start()  # Because first preview capture is longer than others
                first_loop = False

            pygame.event.pump()
            if updated_rect:
                pygame.display.update(updated_rect)

        self._show_overlay(get_translated_text('smile'), alpha)
        self._build_and_display_preview()


        """Show a countdown of `timeout` seconds on the preview.
        Returns when the countdown is finished.
        """
        timeout = int(timeout)
        if timeout < 1:
            raise ValueError("Start time shall be greater than 0")

        while timeout > 0:
            self._show_overlay(timeout, alpha)
            time.sleep(1)
            timeout -= 1
            self._hide_overlay()

        self._show_overlay(get_translated_text('smile'), alpha)

    def stop_preview(self):
        """Stop Preview: do nothing"""
        self._hide_overlay()
        self._window = None

    def capture(self, effect=None):
        """Simulate capture, return path to still image"""
        self._hide_overlay()
        self._captures.append(self._generate_still_image())

    def _post_process_capture(self, capture_data):
        """Rework and return a PIL Image object from capture data.
        """
        image = capture_data
        return image

    def quit(self):
        """Do nothing when quitting"""
