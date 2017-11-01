# -*- coding: utf-8 -*-

import io
import picamera
from PIL import Image


class PtbCamera(object):

    """Camera management
    """

    def __init__(self, iso=200, resolution=(1920, 1080)):
        self._cam = picamera.PiCamera()
        self._cam.video_stabilization = True
        self._cam.vflip = False
        self._cam.resolution = resolution
        self._cam.iso = iso

        # For an obscure reason, the preview position need an offset to the pygame
        # window position (probably the display size is not evaluated in the same way)
        self._pos_margin = 50
        self._border = 50

    def preview(self, rect, flip=True):
        """Display a preview on the given Rect (flip if necessary).
        """
        # (x, y, width, height)
        res = (rect.width - 2 * self._border, rect.height - 2 * self._border)
        window = (rect.left + self._pos_margin + self._border, rect.top + self._pos_margin + self._border,
                  rect.width - 2 * self._border, rect.height - 2 * self._border)
        self._cam.start_preview(resolution=res, hflip=flip, fullscreen=False, window=window)

    def capture(self, filename=None, pil_format='png'):
        """
        Capture a picture in a file. If no filename given a PIL image
        is returned.

        Possible PIL formats are:
            ‘jpeg‘ — Write a JPEG file
            ‘png‘ — Write a PNG file
            ‘gif‘ — Write a GIF file
            ‘bmp‘ — Write a Windows bitmap file
            ‘yuv‘ — Write the raw image data to a file in YUV420 format
            ‘rgb‘ — Write the raw image data to a file in 24-bit RGB format
            ‘rgba‘ — Write the raw image data to a file in 32-bit RGBA format
            ‘bgr‘ — Write the raw image data to a file in 24-bit BGR format
            ‘bgra‘ — Write the raw image data to a file in 32-bit BGRA format
            ‘raw‘ — Deprecated option for raw captures; the format is taken from the
        """
        # Stop preview before flip (avoid headache)
        self._cam.stop_preview()
        if filename:
            self._cam.capture(filename)
            return filename
        else:
            # Create the in-memory stream
            stream = io.BytesIO()
            self._cam.capture(stream, format=pil_format)
            # "Rewind" the stream to the beginning so we can read its content
            stream.seek(0)
            return Image.open(stream)

    def quit(self):
        """Close the camera driver, it's definitive.
        """
        self._cam.close()
