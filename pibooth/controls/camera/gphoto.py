# -*- coding: utf-8 -*-

import io
import os
import time
import signal
import subprocess
try:
    import gphoto2 as gp
except ImportError:
    gp = None  # gphoto2 is optional
from PIL import Image, ImageFilter
from pibooth.pictures import sizing
from pibooth.config.parser import PiConfigParser
from pibooth.utils import LOGGER, PoolingTimer
from pibooth.controls.camera.base import BaseCamera, LANGUAGES


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


class GpCamera(BaseCamera):

    """gPhoto2 camera management.
    """

    IMAGE_EFFECTS = [u'none',
                     u'blur',
                     u'contour',
                     u'detail',
                     u'edge_enhance',
                     u'edge_enhance_more',
                     u'emboss',
                     u'find_edges',
                     u'smooth',
                     u'smooth_more',
                     u'sharpen']

    def __init__(self, iso=200, resolution=(1920, 1080), rotation=0, flip=False):
        BaseCamera.__init__(self, resolution)
        gp.check_result(gp.use_python_logging())

        self._preview_hflip = False
        self._capture_hflip = flip
        self._rotation = rotation
        self._iso = iso
        self.gphoto2_process = None
        self.omxplayer_process = None

    def _init(self):
        """Camera initialisation
        """
        self._cam = gp.Camera()
        self._cam.init()
        config = self._cam.get_config()
        self.set_config_value(config, 'imgsettings', 'iso', self._iso)
        self.set_config_value(config, 'settings', 'capturetarget', 'Memory card')
        self._cam.set_config(config)

    def _show_overlay(self, text, alpha):
        """Add an image as an overlay.
        """
        if self._window:  # No window means no preview displayed
            rect = self._window.get_rect()
            size = (((rect.width + 31) // 32) * 32, ((rect.height + 15) // 16) * 16)

            image = Image.new('RGB', size, color=(0, 0, 0))
            self._overlay = self.build_overlay(image.size, text, alpha)
            image.paste(self._overlay, (0, 0), self._overlay)
            self._window.show_image(image)

    def _post_process_capture(self, capture_path):
        """Rework and return a Image object from file.
        """
        gp_path, effect = self._captures[capture_path]
        camera_file = self._cam.file_get(gp_path.folder, gp_path.name, gp.GP_FILE_TYPE_NORMAL)
        image = Image.open(io.BytesIO(camera_file.get_data_and_size()))
        image = image.crop(sizing.new_size_by_croping_ratio(image.size, self.resolution))

        if self._capture_hflip:
            image = image.transpose(Image.FLIP_LEFT_RIGHT)

        if effect != 'none':
            image = image.filter(getattr(ImageFilter, effect.upper()))

        image.save(capture_path)
        return image

    @staticmethod
    def set_config_value(config, section, option, value):
        """Set camera configuration. This method don't send the updated
        configuration to the camera (avoid connection flooding if several
        values have to be changed)
        """
        try:
            LOGGER.debug('Setting option %s/%s=%s', section, option, value)
            child = config.get_child_by_name(section).get_child_by_name(option)
            choices = [c for c in child.get_choices()]
            data_type = type(child.get_value())
            value = data_type(value)  # Cast value
            if value not in choices:
                LOGGER.warning(
                    "Invalid value '%s' for option %s (possible choices: %s), trying to set it anyway", value, option, choices)
                child.set_value(value)
            else:
                child.set_value(value)
        except gp.GPhoto2Error:
            LOGGER.error('Unsupported setting %s/%s=%s (please configure your DSLR manually)', section, option, value)

    def preview(self, window, flip=True):
        """Setup the preview.
        """
        self._window = window
        self.gphoto2_process = True  # hack to avoid the preview
        if not self.gphoto2_process:
            rect = self.get_rect()
            if flip:
                orientation = 1
            else:
                orientation = 0
            self.gphoto2_process = subprocess.Popen("gphoto2 --capture-movie --stdout> fifo.mjpg &",
                                                    shell=True,
                                                    preexec_fn=os.setsid)
            window_rect = '{0},{1},{2},{3}'.format(tuple(rect)[0], tuple(rect)[1], tuple(rect)[0] + tuple(rect)[2],
                                                   tuple(rect)[1] + tuple(rect)[3])
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

        timer = PoolingTimer(timeout)
        while not timer.is_timeout():
            self.preview(self._window)
            remaining = int(timer.remaining() + 1)
            if not self._overlay or remaining != timeout:
                # Rebluid overlay only if remaining number has changed
                self._show_overlay(str(remaining), alpha)
                timeout = remaining

        self._show_overlay(LANGUAGES.get(PiConfigParser.language, LANGUAGES['en']).get('smile_message'), alpha)

    def preview_wait(self, timeout, alpha=60):
        """Wait the given time.
        """
        time.sleep(timeout)
        self._show_overlay(LANGUAGES.get(PiConfigParser.language, LANGUAGES['en']).get('smile_message'), alpha)

    def stop_preview(self):
        """Stop the preview.
        """
        if self.omxplayer_process:
            os.killpg(os.getpgid(self.omxplayer_process.pid), signal.SIGTERM)
            self.omxplayer_process = None
        self._window = None

    def capture(self, filename, effect=None):
        """Capture a picture in a file.
        """
        effect = str(effect).lower()
        if effect not in self.IMAGE_EFFECTS:
            raise ValueError("Invalid capture effect '{}' (choose among {})".format(effect, self.IMAGE_EFFECTS))

        self._init()
        self._captures[filename] = (self._cam.capture(gp.GP_CAPTURE_IMAGE), effect)
        time.sleep(1)  # Necessary to let the time for the camera to save the image
        self.quit()

        self._hide_overlay()  # If stop_preview() has not been called

    def quit(self):
        """Close the camera driver, it's definitive.
        """
        if self._cam:
            self._cam.exit()
