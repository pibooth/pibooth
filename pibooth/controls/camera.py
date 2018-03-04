# -*- coding: utf-8 -*-


import io
import time
import subprocess
import picamera
try:
    import gphoto2 as gp
except ImportError:
    gp = None  # gphoto2 is optional
from PIL import Image, ImageFont, ImageDraw
from pibooth import pictures, fonts
from pibooth.utils import LOGGER, PoolingTimer


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
    if not gp:
        return False  # gphoto2 is not installed
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
        self._cam.vflip = False
        self._cam.resolution = resolution
        self._cam.iso = iso
        self._cam.rotation = rotation

        self._border = 50
        self._preview_window = None

    def preview(self, window, flip=True):
        """Display a preview on the given Rect (flip if necessary).
        """
        rect = window.get_rect()
        res = pictures.resize_keep_aspect_ratio(self._cam.resolution,
                                                (rect.width - 2 * self._border, rect.height - 2 * self._border))
        # (x, y, width, height)
        self._preview_window = (rect.centerx - res[0] // 2, rect.centery - res[1] // 2, res[0], res[1])
        self._cam.start_preview(resolution=res, hflip=flip, fullscreen=False, window=self._preview_window)

    def preview_countdown(self, timeout, alpha=60):
        """Show a countdown of `timeout` seconds on the preview.
        Returns when the countdown is finished.
        """
        timeout = int(timeout)
        if timeout < 1:
            raise ValueError("Start time shall be greater than 0")
        if not self._cam.preview:
            raise EnvironmentError("Preview shall be started first")

        # Create an image padded to the required size
        size = (((self._preview_window[2] + 31) // 32) * 32,
                ((self._preview_window[3] + 15) // 16) * 16)

        font = ImageFont.truetype(fonts.get_filename("Amatic-Bold.ttf"), size[1] * 8 // 10)

        while timeout > 0:
            txt = str(timeout)
            image = Image.new('RGBA', size)
            draw = ImageDraw.Draw(image)
            txt_width, txt_height = draw.textsize(txt, font=font)
            position = ((size[0] - txt_width) // 2, (size[1] - txt_height) // 2 - size[1] // 10)
            draw.text(position, txt, (255, 255, 255, alpha), font=font)
            overlay = self._cam.add_overlay(image.tobytes(), image.size, layer=3,
                                            window=self._preview_window, fullscreen=False)
            time.sleep(1)
            timeout -= 1
            self._cam.remove_overlay(overlay)

    def preview_wait(self, timeout):
        """Wait the given time.
        """
        time.sleep(timeout)

    def stop_preview(self):
        """Stop the preview.
        """
        self._cam.stop_preview()
        self._preview_window = None

    def capture(self, filename=None, pil_format='png'):
        """Capture a picture in a file. If no filename given a PIL image
        is returned.
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
        self._config = self._cam.get_config()
        self._resolution = resolution

        self._window = None  # Window where the preview is displayed
        self._vflip = False
        self._border = 50

        self._set_config_value('imgsettings', 'iso', iso)

    def _set_config_value(self, section, option, value):
        for child in self._config.get_children():
            if child.get_name() == section:
                for subchild in child.get_children():
                    if subchild.get_name() == option:
                        LOGGER.debug('Set %s (%s/%s) to %s', subchild.get_label(),
                                     child.get_name(), subchild.get_name(), value)
                        subchild.set_value(str(value))
                        return
        raise ValueError('Unsupported setting {}/{}'.format(section, option))

    def _get_preview_image(self):
        camera_file = self._cam.capture_preview()
        file_data = gp.check_result(gp.gp_file_get_data_and_size(camera_file))
        image = Image.open(io.BytesIO(memoryview(file_data)))
        if self._vflip:
            image = image.transpose(Image.FLIP_LEFT_RIGHT)

        return image.resize(self.get_rect())

    def get_rect(self):
        """Return the available surface to display image.
        """
        rect = self._window.get_rect()
        return pictures.resize_keep_aspect_ratio(self._resolution,
                                                 (rect.width - 2 * self._border, rect.height - 2 * self._border))

    def preview(self, window, flip=True):
        self._window = window
        self._vflip = flip
        LOGGER.debug('Capturing new preview image')
        self._window.show_image(self._get_preview_image())

    def preview_countdown(self, timeout, alpha=60):
        """Show a countdown of `timeout` seconds on the preview.
        Returns when the countdown is finished.
        """
        timeout = int(timeout)
        if timeout < 1:
            raise ValueError("Start time shall be greater than 0")

        size = self.get_rect()
        font = ImageFont.truetype(fonts.get_filename("Amatic-Bold.ttf"), size[1] * 8 // 10)

        timer = PoolingTimer(timeout)
        while not timer.is_timeout():
            txt = str(int(timer.remaining() + 1))
            image = self._get_preview_image()
            overlay = Image.new('RGBA', image.size)
            draw = ImageDraw.Draw(overlay)
            txt_width, txt_height = draw.textsize(txt, font=font)
            position = ((size[0] - txt_width) // 2, (size[1] - txt_height) // 2 - size[1] // 10)
            draw.text(position, txt, (255, 255, 255, alpha), font=font)
            image.paste(overlay, (0, 0), overlay)
            self._window.show_image(image)

    def preview_wait(self, timeout):
        """Wait the given time and refresh the preview.
        """
        timeout = int(timeout)
        if timeout < 1:
            raise ValueError("Start time shall be greater than 0")

        timer = PoolingTimer(timeout)
        while not timer.is_timeout():
            self._window.show_image(self._get_preview_image())

    def stop_preview(self):
        """Stop the preview.
        """
        self._window = None

    def capture(self, filename=None, pil_format='png'):
        """Capture a picture in a file. If no filename given a PIL image
        is returned.
        """
        camera_file = self._cam.capture_preview()
        file_data = gp.check_result(gp.gp_file_get_data_and_size(camera_file))
        image = Image.open(io.BytesIO(memoryview(file_data)))

        if self._vflip:
            self._window.show_image(image.transpose(Image.FLIP_LEFT_RIGHT).resize(self.get_rect()))
        else:
            self._window.show_image(image.resize(self.get_rect()))
        if filename:
            image.save(filename)
            return filename
        else:
            return image

    def quit(self):
        """Close the camera driver, it's definitive.
        """
        self._cam.exit()
