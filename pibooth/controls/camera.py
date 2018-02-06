# -*- coding: utf-8 -*-


import io
import subprocess
import picamera
import gphoto2 as gp
from PIL import Image
from pibooth import pictures


def rpi_camera_connected():
    """Return True if a RPi camera is found.
    """
    try:
        process = subprocess.Popen(['vcgencmd', 'get_camera'],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, _stderr = process.communicate()
        if stdout and u'detected=1' in stdout.decode('utf-8'):
            return True
    except OSError:
        pass
    return False


def gp_camera_connected():
    """Return True if a camera compatible with gphoto2 is found.
    """
    if hasattr(gp, 'gp_camera_autodetect'):
        # gphoto2 version 2.5+
        cameras = gp.check_result(gp.gp_camera_autodetect())
    else:
        port_info_list = gp.PortInfoList()
        port_info_list.load()
        abilities_list = gp.CameraAbilitiesList()
        abilities_list.load()
        cameras = abilities_list.detect(port_info_list)
    if cameras:
        return True

    return False


class RpiCamera(object):

    """Camera management
    """

    def __init__(self, iso=200, resolution=(1920, 1080), rotation=0):
        self._cam = picamera.PiCamera()
        self._cam.framerate = 15  # Slower is necessary for high-resolution
        self._cam.video_stabilization = True
        self._cam.preview_alpha = 251  # Necessary to show countdown by transparency
        self._cam.vflip = False
        self._cam.resolution = resolution
        self._cam.iso = iso
        self._cam.rotation = rotation

        self._border = 50

    def preview(self, rect, flip=True):
        """Display a preview on the given Rect (flip if necessary).
        """
        res = pictures.resize_keep_aspect_ratio(self._cam.resolution,
                                                (rect.width - 2 * self._border, rect.height - 2 * self._border))

        # (x, y, width, height)
        win = (rect.centerx - res[0] // 2, rect.centery - res[1] // 2, res[0], res[1])
        self._cam.start_preview(resolution=res, hflip=flip, fullscreen=False, window=win)

    def stop_preview(self):
        """Stop the preview.
        """
        self._cam.stop_preview()

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


class GpCamera(object):

    """Gphoto2 camera management.
    """

    def __init__(self, iso=200, resolution=(1920, 1080), rotation=0):
        gp.check_result(gp.use_python_logging())
        self._cam = gp.Camera()
        self._cam.init()

    def preview(self, rect, flip=True):
        pass  # Is it possible?

    def stop_preview(self):
        pass

    def capture(self, filename=None, pil_format='png'):
        camera_file = self._cam.capture_preview()
        file_data = self._cam.file_get_data_and_size(camera_file)
        image = Image.open(io.BytesIO(file_data))
        if filename:
            image.save(filename)
            return filename
        else:
            return image

    def quit(self):
        self._cam.exit()
