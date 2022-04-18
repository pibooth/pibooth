# -*- coding: utf-8 -*-

import sys
import threading
import pygame
from PIL import Image, ImageDraw

from pibooth import fonts
from pibooth.pictures import sizing


EVT_CAMERA_PREVIEW = pygame.USEREVENT + 3
EVT_CAMERA_CAPTURE = pygame.USEREVENT + 4


class CameraWorker(threading.Thread):

    def __init__(self, event_type, getter, args=(), loop=True):
        super(CameraWorker, self).__init__(name='CameraWorker')
        self.daemon = True
        self.get_capture = getter
        self.event_type = event_type
        self._args = args
        self._loop = loop
        self._stop_request = threading.Event()

    def emit(self, capture, exc_info=None):
        """Post event with the new capture.
        """
        event = pygame.event.Event(self.event_type, image=capture, error=exc_info)
        pygame.event.post(event)

    def run(self):
        try:
            while not self._stop_request.is_set():
                self.emit(self.get_capture(*self._args))
                if not self._loop:
                    break
        except:
            self.emit(None, sys.exc_info())

    def kill(self):
        """Stop working.
        """
        self._stop_request.set()
        self.join(5)


class BaseCamera(object):

    IMAGE_EFFECTS = ['none']

    def __init__(self, camera_proxy):
        self._cam = camera_proxy
        self._rect = None
        self._overlay = None
        self._overlay_text = None
        self._overlay_alpha = 60
        self._captures = []
        self._worker = None

        self.resolution = None
        self.delete_internal_memory = False
        self.preview_rotation, self.capture_rotation = (0, 0)
        self.preview_iso, self.capture_iso = (100, 100)
        self.preview_flip, self.capture_flip = (False, False)

    def initialize(self, iso, resolution, rotation=0, flip=False, delete_internal_memory=False):
        """Initialize the camera.
        """
        if not isinstance(rotation, (tuple, list)):
            rotation = (rotation, rotation)
        self.preview_rotation, self.capture_rotation = rotation
        for name in ('preview', 'capture'):
            rotation = getattr(self, '{}_rotation'.format(name))
            if rotation not in (0, 90, 180, 270):
                raise ValueError(
                    "Invalid {} camera rotation value '{}' (should be 0, 90, 180 or 270)".format(name, rotation))
        self.resolution = resolution
        self.capture_flip = flip
        if not isinstance(iso, (tuple, list)):
            iso = (iso, iso)
        self.preview_iso, self.capture_iso = iso
        self.delete_internal_memory = delete_internal_memory
        self._specific_initialization()

    def _specific_initialization(self):
        """Specific camera initialization.
        """
        pass

    def set_overlay(self, text, alpha=60):
        """Show a text over on the preview.
        """
        if self._rect is None:
            raise IOError("Preview is not started")
        if text is None:
            self._hide_overlay()
        elif str(text) != self._overlay_text:
            self._overlay_text = str(text)
            self._overlay_alpha = alpha
            self._show_overlay()

    def build_overlay(self, size, text, alpha):
        """Return a PIL image with the given text that can be used
        as an overlay for the camera.
        """
        image = Image.new('RGBA', size)
        draw = ImageDraw.Draw(image)

        font = fonts.get_pil_font(text, fonts.CURRENT, 0.9 * size[0], 0.9 * size[1])
        txt_width, txt_height = draw.textsize(text, font=font)

        position = ((size[0] - txt_width) // 2, (size[1] - txt_height) // 2 - size[1] // 10)
        draw.text(position, text, (255, 255, 255, alpha), font=font)
        return image

    def _show_overlay(self):
        """Add an image as an overlay.
        """
        self._overlay = self.build_overlay(self._rect.size,
                                           self._overlay_text,
                                           self._overlay_alpha)

    def _hide_overlay(self):
        """Remove any existing overlay.
        """
        if self._overlay is not None:
            self._overlay = None
            self._overlay_text = None

    def get_preview_image(self):
        """Return a new image fit to the preview rect.
        """
        raise NotImplementedError

    def preview(self, rect, flip=True):
        """Start the preview fitting the given Rect object.
        """
        if self._worker and self._worker.is_alive():
            # Already running
            return

        # Define Rect() object for resizing preview captures to fit to the defined
        # preview rect keeping same aspect ratio than camera resolution.
        size = sizing.new_size_keep_aspect_ratio(self.resolution, (rect.width, rect.height))
        self._rect = pygame.Rect(rect.centerx - size[0] // 2, rect.centery - size[1] // 2, size[0], size[1])

        self.preview_flip = flip
        self._worker = CameraWorker(EVT_CAMERA_PREVIEW, self.get_preview_image)
        self._worker.start()

    def stop_preview(self):
        """Stop the preview.
        """
        self._rect = None
        if self._worker:
            self._worker.kill()
            self._worker = None
        self._hide_overlay()

    def _process_capture(self, capture_data):
        """Rework and return a PIL Image object from capture data.
        """
        raise NotImplementedError

    def get_capture_image(self, effect=None):
        """Return a new full resolution image.
        """
        raise NotImplementedError

    def capture(self, effect=None, wait=False):
        """Take a new capture and add it to internal buffer.
        """
        effect = str(effect).lower()
        if effect not in self.IMAGE_EFFECTS:
            raise ValueError("Invalid capture effect '{}' (choose among {})".format(effect, self.IMAGE_EFFECTS))

        if self._worker:
            self.stop_preview()

        self._worker = CameraWorker(EVT_CAMERA_CAPTURE, self.get_capture_image, (effect,), False)
        self._worker.start()
        if wait:
            self._worker.join()

    def grab_captures(self):
        """Return all buffered captures as PIL images (buffer dropped after call).
        """
        images = []
        for data in self._captures:
            images.append(self._process_capture(data))
        self.drop_captures()
        return images

    def drop_captures(self):
        """Delete all buffered captures.
        """
        self._captures.clear()

    def quit(self):
        """Close the camera driver, it's definitive.
        """
        if self._worker:
            self._worker.kill()
        self._specific_cleanup()

    def _specific_cleanup(self):
        """Specific camera cleanup.
        """
        pass
