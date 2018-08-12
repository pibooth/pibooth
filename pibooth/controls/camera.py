# -*- coding: utf-8 -*-

import io
import os
import time
import signal
import subprocess
import pygame
import picamera
try:
    import gphoto2 as gp
except ImportError:
    gp = None  # gphoto2 is optional
from PIL import Image, ImageFont, ImageDraw
from pibooth import fonts
from pibooth.pictures import sizing
from pibooth.utils import LOGGER, PoolingTimer, timeit


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
    """Return True if a camera compatible with gPhoto2 is found.
    """
    if not gp:
        return False  # gPhoto2 is not installed
    if hasattr(gp, 'gp_camera_autodetect'):
        # gPhoto2 version 2.5+
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


def gp_set_config_value(config, section, option, value):
    """Set camera configuration. This method don't send the updated
    configuration to the camera (avoid connection flooding if several
    values have to be changed)
    """
    try:
        LOGGER.debug('Setting option %s/%s=%s', section, option, value)
        child = config.get_child_by_name(section).get_child_by_name(option)
        choices = [c for c in child.get_choices()]
        if value not in choices:
            LOGGER.warning(
                "Invalid value '%s' for option %s (possible choices: %s), still trying to set it", value, option, choices)
            child.set_value(str(value))
        else:
            child.set_value(str(value))
    except gp.GPhoto2Error:
        raise ValueError('Unsupported setting {}/{}={}'.format(section, option, value))


class BaseCamera(object):

    def __init__(self, resolution):
        self._cam = None
        self._border = 50
        self._window = None
        self._captures = {}
        self.resolution = resolution

    def _post_process_capture(self, capture_path):
        """Rework and return a capture from file.
        """
        return Image.open(capture_path)

    def get_rect(self):
        """Return a Rect object (as defined in pygame) for resizing preview and images
        in order to fit to the defined window.
        """
        rect = self._window.get_rect()
        res = sizing.new_size_keep_aspect_ratio(self.resolution,
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

    def get_captures(self):
        """Return all buffered captures as PIL images (buffer dropped after call).
        """
        images = []
        for path in sorted(self._captures):
            images.append(self._post_process_capture(path))
        self.drop_captures()
        return images

    def drop_captures(self):
        """Delete all buffered captures.
        """
        self._captures = {}


class RpiCamera(BaseCamera):

    """Camera management
    """

    def __init__(self, iso=200, resolution=(1920, 1080), rotation=0, flip=False):
        BaseCamera.__init__(self, resolution)
        self._cam = picamera.PiCamera()
        self._cam.framerate = 15  # Slower is necessary for high-resolution
        self._cam.video_stabilization = True
        self._cam.vflip = False
        self._cam.hflip = flip
        self._cam.resolution = resolution
        self._cam.iso = iso
        self._cam.rotation = rotation

    def preview(self, window, flip=True):
        """Display a preview on the given Rect (flip if necessary).
        """
        self._window = window
        rect = self.get_rect()
        if self._cam.hflip:
            if flip:
                 # Don't flip again, already done at init
                flip = False
            else:
                # Flip again because flipped once at init
                flip = True
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

    def capture(self, filename):
        """Capture a picture in a file.
        """
        self._cam.capture(filename)
        self._captures[filename] = None  # Nothing to keep for post processing

    def quit(self):
        """Close the camera driver, it's definitive.
        """
        self._cam.close()


class GpCamera(BaseCamera):

    """gPhoto2 camera management.
    """

    def __init__(self, iso=200, resolution=(1920, 1080), rotation=0, flip=False):
        BaseCamera.__init__(self, resolution)
        gp.check_result(gp.use_python_logging())

        self._preview_hflip = False
        self._capture_hflip = flip
        self._rotation = rotation
        self._iso = str(iso)
        self.gphoto2_process = None
        self.omxplayer_process = None

    def _init(self):
        """Camera initialisation
        """
        self._cam = gp.Camera()
        self._cam.init()
        config = self._cam.get_config()
        gp_set_config_value(config, 'imgsettings', 'iso', self._iso)
        gp_set_config_value(config, 'settings', 'capturetarget', 'Carte mémoire')
        self._cam.set_config(config)

    def _post_process_capture(self, capture_path):
        gp_path = self._captures[capture_path]
        camera_file = gp.check_result(gp.gp_camera_file_get(
            self._cam, gp_path.folder, gp_path.name, gp.GP_FILE_TYPE_NORMAL))

        image = Image.open(io.BytesIO(memoryview(camera_file.get_data_and_size())))
        image = image.resize(sizing.new_size_keep_aspect_ratio(image.size, self.resolution, 'outer'), Image.ANTIALIAS)
        image = image.crop(sizing.new_size_by_croping(image.size, self.resolution))

        if self._capture_hflip:
            image = image.transpose(Image.FLIP_LEFT_RIGHT)
        image.save(capture_path)
        return image

    def preview(self, window, flip=True, timeout=5):
        """Setup the preview.
        """
        if not self.gphoto2_process:
            self._window = window
            rect = self.get_rect()
            if flip:
                orientation = 1
            else:
                orientation = 0
            self.gphoto2_process = subprocess.Popen("gphoto2 --capture-movie --stdout> fifo.mjpg &",
                                                    shell=True,
                                                    preexec_fn=os.setsid)
            window_rect = '{0},{1},{2},{3}'.format(tuple(rect)[0], tuple(rect)[1], tuple(rect)[
                                                   0] + tuple(rect)[2], tuple(rect)[1] + tuple(rect)[3])
            command = "omxplayer fifo.mjpg --live --crop 252,0,804,704 --win {0} --orientation {1}".format(
                window_rect, orientation)
            self.omxplayer_process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True, preexec_fn=os.setsid)

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
            self.preview(self._window)
            remaining = int(timer.remaining() + 1)
            if not overlay or remaining != timeout:
                # Rebluid overlay only if remaining number has changed
                # overlay = self.get_overlay(image.size, str(remaining), alpha)
                timeout = remaining
            #image.paste(overlay, (0, 0), overlay)
            # self._window.show_image(image)

    def preview_wait(self, timeout):
        """Wait the given time and refresh the preview.
        """
        timeout = int(timeout)
        if timeout < 1:
            raise ValueError("Start time shall be greater than 0")

        timer = PoolingTimer(timeout)
        while not timer.is_timeout():
            self.preview(self._window, timeout=timeout)

    def stop_preview(self):
        """Stop the preview.
        """
        if self.gphoto2_process:
            os.killpg(os.getpgid(self.gphoto2_process.pid), signal.SIGTERM)
            self.gphoto2_process = None
        if self.omxplayer_process:
            os.killpg(os.getpgid(self.omxplayer_process.pid), signal.SIGTERM)
            self.omxplayer_process = None
        self._window = None

    def capture(self, filename):
        """Capture a picture in a file.
        """
        self._init()
        self._captures[filename] = self._cam.capture(gp.GP_CAPTURE_IMAGE)
        time.sleep(1)  # Necessary to let the time for the camera to save the image
        self.quit()

    def quit(self):
        """Close the camera driver, it's definitive.
        """
        if self._cam:
            self._cam.exit()


class HybridCamera(RpiCamera):

    """Camera management using the Raspberry Pi camera for the preview (better
    video rendering) and a gPhoto2 compatible camera for the capture (higher
    resolution)
    """

    def __init__(self, *args, **kwargs):
        RpiCamera.__init__(self, *args, **kwargs)
        gp.check_result(gp.use_python_logging())
        self._gp_cam = gp.Camera()
        self._gp_cam.init()

        config = self._gp_cam.get_config()
        gp_set_config_value(config, 'imgsettings', 'iso', self._cam.iso)
        gp_set_config_value(config, 'settings', 'capturetarget', 'Carte mémoire')
        self._gp_cam.set_config(config)

    def _post_process_capture(self, capture_path):
        gp_path = self._captures[capture_path]
        camera_file = gp.check_result(gp.gp_camera_file_get(
            self._gp_cam, gp_path.folder, gp_path.name, gp.GP_FILE_TYPE_NORMAL))

        image = Image.open(io.BytesIO(memoryview(camera_file.get_data_and_size())))
        image = image.resize(sizing.new_size_keep_aspect_ratio(
            image.size, self._cam.resolution, 'outer'), Image.ANTIALIAS)
        image = image.crop(sizing.new_size_by_croping(image.size, self._cam.resolution))

        if self._cam.hflip:
            image = image.transpose(Image.FLIP_LEFT_RIGHT)
        image.save(capture_path)
        return image

    def capture(self, filename):
        """Capture a picture in a file.
        """
        RpiCamera.capture(self, filename)  # Just to show a captured image at screen
        self._captures[filename] = self._gp_cam.capture(gp.GP_CAPTURE_IMAGE)
        time.sleep(1)  # Necessary to let the time for the camera to save the image

    def quit(self):
        """Close the camera driver, it's definitive.
        """
        RpiCamera.quit(self)
        self._gp_cam.exit()
