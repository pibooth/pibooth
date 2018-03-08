# -*- coding: utf-8 -*-


import io
import time
import subprocess
import pygame
import picamera
try:
    import gphoto2 as gp
except ImportError:
    gp = None  # gphoto2 is optional
from PIL import Image, ImageFont, ImageDraw
from pibooth import pictures, fonts
from pibooth.utils import LOGGER, PoolingTimer, timeit


def rpi_camera_connected():
    """Return True if a RPi camera is found.
    """
    return False
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


class BaseCamera(object):

    def __init__(self, resolution):
        self._cam = None
        self._border = 50
        self._window = None
        self.resolution = resolution

    def get_rect(self):
        """Return a Rect object (as defined in pygame) for resizing preview and images
        in order to fit to the defined window.
        """
        rect = self._window.get_rect()
        res = pictures.resize_keep_aspect_ratio(self.resolution,
                                                (rect.width - 2 * self._border, rect.height - 2 * self._border))
        return pygame.Rect(rect.centerx - res[0] // 2, rect.centery - res[1] // 2, res[0], res[1])

    def get_overlay(self, size, text, alpha):
        """Return a PIL image with the given text that can be used
        as an overlay for the camera.
        """
        font = ImageFont.truetype(fonts.get_filename("Amatic-Bold.ttf"), size[1] * 8 // 10)
        image = Image.new('RGBA', size)
        draw = ImageDraw.Draw(image)
        txt_width, txt_height = draw.textsize(text, font=font)
        position = ((size[0] - txt_width) // 2, (size[1] - txt_height) // 2 - size[1] // 10)
        draw.text(position, text, (255, 255, 255, alpha), font=font)
        return image


class RpiCamera(BaseCamera):

    """Camera management
    """

    def __init__(self, iso=200, resolution=(1920, 1080), rotation=0):
        BaseCamera.__init__(self, resolution)
        self._cam = picamera.PiCamera()
        self._cam.framerate = 15  # Slower is necessary for high-resolution
        self._cam.video_stabilization = True
        self._cam.vflip = False
        self._cam.resolution = resolution
        self._cam.iso = iso
        self._cam.rotation = rotation

    def preview(self, window, flip=True):
        """Display a preview on the given Rect (flip if necessary).
        """
        self._window = window
        rect = self.get_rect()
        self._cam.start_preview(resolution=(rect.width, rect.height), hflip=flip,
                                fullscreen=False, window=tuple(rect))

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
        rect = self.get_rect()
        size = (((rect.width + 31) // 32) * 32, ((rect.height + 15) // 16) * 16)

        while timeout > 0:
            image = self.get_overlay(size, str(timeout), alpha)
            overlay = self._cam.add_overlay(image.tobytes(), image.size, layer=3,
                                            window=tuple(rect), fullscreen=False)
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
        self._window = None

    def capture(self, filename=None, flip=True):
        """Capture a picture in a file. If no filename given a PIL image
        is returned.
        """
        if self._cam.hflip != flip:
            self._cam.hflip = flip
        if filename:
            self._cam.capture(filename)
            return filename
        else:
            # Create the in-memory stream
            stream = io.BytesIO()
            self._cam.capture(stream)
            # "Rewind" the stream to the beginning so we can read its content
            stream.seek(0)
            return Image.open(stream)

    def quit(self):
        """Close the camera driver, it's definitive.
        """
        self._cam.close()


class GpCamera(BaseCamera):

    """Gphoto2 camera management.
    """

    def __init__(self, iso=200, resolution=(1920, 1080), rotation=0):
        BaseCamera.__init__(self, resolution)
        gp.check_result(gp.use_python_logging())
        self._cam = gp.Camera()
        self._cam.init()
        self._config = self._cam.get_config()

        self._preview_hflip = False
        self._rotation = rotation
        self._set_config_value('imgsettings', 'iso', iso)
        self._cam.set_config(self._config)

    def _set_config_value(self, section, option, value):
        """Set camera configuration. This method dont send the updated
        configuration to the camera (avoid connection flooding if several
        values to be changed)
        """
        try:
            LOGGER.debug('Setting option %s/%s=%s', section, option, value)
            child = self._config.get_child_by_name(section).get_child_by_name(option)
            choices = [c for c in child.get_choices()]
            if not choices or value in choices:
                child.set_value(str(value))
            else:
                LOGGER.warning("Invalid value '%s' for option %s (possible choices: %s)", value, option, choices)
        except gp.GPhoto2Error:
            raise ValueError('Unsupported setting {}/{}={}'.format(section, option, value))

    def _get_preview_image(self):
        """Capture a new preview image.
        """
        with timeit('Capturing new preview image'):
            camera_file = self._cam.capture_preview()
            file_data = gp.check_result(gp.gp_file_get_data_and_size(camera_file))
            image = Image.open(io.BytesIO(memoryview(file_data)))
            if self._preview_hflip:
                image = image.transpose(Image.FLIP_LEFT_RIGHT)

            image = image.resize(pictures.resize_keep_aspect_ratio(image.size, self.resolution, 'outer'))
            image = image.crop(pictures.resize_by_croping(image.size, self.resolution))

        # Resize to the window rect (outer because rect already resized innner, see 'get_rect')
        rect = self.get_rect()
        return image.resize(pictures.resize_keep_aspect_ratio(image.size,  (rect.width, rect.height), 'outer'))

    def preview(self, window, flip=True):
        """Setup the preview.
        """
        self._window = window
        self._preview_hflip = flip
        self._window.show_image(self._get_preview_image())

    def preview_countdown(self, timeout, alpha=60):
        """Show a countdown of `timeout` seconds on the preview.
        Returns when the countdown is finished.
        """
        timeout = int(timeout)
        if timeout < 1:
            raise ValueError("Start time shall be greater than 0")

        overlay = None
        timer = PoolingTimer(timeout)
        while not timer.is_timeout():
            image = self._get_preview_image()
            remaining = int(timer.remaining() + 1)
            if not overlay or remaining != timeout:
                # Rebluid overlay only if remaining number has changed
                overlay = self.get_overlay(image.size, str(remaining), alpha)
                timeout = remaining
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

    def capture(self, filename=None, flip=True):
        """Capture a picture in a file. If no filename given a PIL image
        is returned.
        """
        camera_file = self._cam.capture_preview()
        file_data = gp.check_result(gp.gp_file_get_data_and_size(camera_file))
        image = Image.open(io.BytesIO(memoryview(file_data)))
        image = image.resize(pictures.resize_keep_aspect_ratio(image.size, self.resolution, 'outer'), Image.ANTIALIAS)
        image = image.crop(pictures.resize_by_croping(image.size, self.resolution))

        # Resize to the window rect (outer because rect already resized innner, see 'get_rect')
        rect = self.get_rect()
        size = pictures.resize_keep_aspect_ratio(image.size,  (rect.width, rect.height), 'outer')

        if self._preview_hflip:
            self._window.show_image(image.transpose(Image.FLIP_LEFT_RIGHT).resize(size))
        else:
            self._window.show_image(image.resize(size))

        if flip:
            image = image.transpose(Image.FLIP_LEFT_RIGHT)
        if filename:
            image.save(filename)
            return filename
        else:
            return image

    def quit(self):
        """Close the camera driver, it's definitive.
        """
        self._cam.exit()
