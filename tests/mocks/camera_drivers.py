# -*- coding: utf-8 -*-


import io
from PIL import Image


class RpiCameraProxyMock:

    MAX_RESOLUTION = (3280, 2464)

    def __init__(self, fake_captures):
        self.preview = None
        self.fake_captures = fake_captures

    def add_overlay(imagebytes, size, layer=3, window=tuple(), fullscreen=False):
        return object()

    def remove_overlay(self, overlay):
        pass

    def start_preview(self, resolution=tuple(), hflip=False, fullscreen=False, window=tuple()):
        self.preview = object()

    def stop_preview(self):
        self.preview = None

    def capture(self, stream, format='jpeg'):
        im = Image.open(self.fake_captures[0])
        im.save(stream, format=format)

    def close(self):
        pass


class GpCameraProxyMock:

    def __init__(self):
        pass
