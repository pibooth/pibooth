# -*- coding: utf-8 -*-

import io
import picamera
from PIL import Image


class PtbCamera(object):

    """Camera management
    """

    def __init__(self, size, camera_iso=200, high_resolution=True):
        self._cam = picamera.PiCamera()
        self._cam.video_stabilization = True
        self._cam.vflip = False
        self._cam.iso = camera_iso
        self.size = size

        if high_resolution:
            # Set camera resolution to high resolution
            self._cam.resolution = (3280, 2464)
        else:
            # Set camera resolution to low resolution
            pixel_width = 500
            self._cam.resolution = (pixel_width, size[1] * size[0] // size[0])

    def preview(self, flip=True):
        """Launch preview (flip if necessary).
        """
        # (x, y, width, height)
        res = (self.size[0] * 80 // 100, self.size[1] * 80 // 100)
        window = (self.size[0] * 10 // 100, self.size[1] * 10 // 100, res[0], res[1])
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
