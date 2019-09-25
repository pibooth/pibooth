# -*- coding: utf-8 -*-

import io
import time
import pygame
try:
    import gphoto2 as gp
except ImportError:
    gp = None  # gphoto2 is optional
from PIL import Image, ImageFilter
from pibooth.utils import memorize
from pibooth.pictures import sizing
from pibooth.config import PiConfigParser
from pibooth.utils import LOGGER, PoolingTimer
from pibooth.controls.camera.base import BaseCamera, LANGUAGES


@memorize
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

    def __init__(self,
                 iso=200,
                 resolution=(1920, 1080),
                 rotation=0,
                 flip=False,
                 delete_internal_memory=False,
                 init=True):
        BaseCamera.__init__(self, resolution, delete_internal_memory)
        gp.check_result(gp.use_python_logging())
        self._preview_compatible = True
        self._preview_hflip = False
        self._capture_hflip = flip
        self._rotation = rotation
        self._iso = iso

        if init:
            self._initialize()

    def _initialize(self):
        """Camera initialisation
        """
        self._cam = gp.Camera()
        self._cam.init()

        try:
            self.get_config_value('actions', 'viewfinder')
            self._preview_compatible = True
        except ValueError:
            LOGGER.warning("The connected DSLR camera is not compatible with preview")
            self._preview_compatible = False
        self.set_config_value('imgsettings', 'iso', self._iso)
        self.set_config_value('settings', 'capturetarget', 'Memory card')

    def _show_overlay(self, text, alpha):
        """Add an image as an overlay.
        """
        if self._window:  # No window means no preview displayed
            rect = self.get_rect()
            self._overlay = self.build_overlay((rect.width, rect.height), str(text), alpha)

    def _get_preview_image(self):
        """Capture a new preview image.
        """
        rect = self.get_rect()
        if self._preview_compatible:
            cam_file = self._cam.capture_preview()
            image = Image.open(io.BytesIO(cam_file.get_data_and_size()))
            # Crop to keep aspect ratio of the resolution
            image = image.crop(sizing.new_size_by_croping_ratio(image.size, self.resolution))
            # Resize to fit the available space in the window
            image = image.resize(sizing.new_size_keep_aspect_ratio(image.size, (rect.width, rect.height), 'outer'))

            if self._preview_hflip:
                image = image.transpose(Image.FLIP_LEFT_RIGHT)
        else:
            image = Image.new('RGB', (rect.width, rect.height), color=(0, 0, 0))

        if self._overlay:
            image.paste(self._overlay, (0, 0), self._overlay)
        return image

    def _post_process_capture(self, capture_path):
        """Rework and return a Image object from file.
        """
        gp_path, effect = self._captures[capture_path]
        camera_file = self._cam.file_get(gp_path.folder, gp_path.name, gp.GP_FILE_TYPE_NORMAL)
        if self.delete_internal_memory:
            LOGGER.debug("Delete capture '%s' from internal memory", gp_path.name)
            self._cam.file_delete(gp_path.folder, gp_path.name)
        image = Image.open(io.BytesIO(camera_file.get_data_and_size()))

        # Crop to keep aspect ratio of the resolution
        image = image.crop(sizing.new_size_by_croping_ratio(image.size, self.resolution))
        # Resize to fit the resolution
        image = image.resize(sizing.new_size_keep_aspect_ratio(image.size, self.resolution, 'outer'))

        if self._capture_hflip:
            image = image.transpose(Image.FLIP_LEFT_RIGHT)

        if effect != 'none':
            image = image.filter(getattr(ImageFilter, effect.upper()))

        image.save(capture_path)
        return image

    def set_config_value(self, section, option, value):
        """Set camera configuration. This method don't send the updated
        configuration to the camera (avoid connection flooding if several
        values have to be changed)
        """
        try:
            LOGGER.debug('Setting option %s/%s=%s', section, option, value)
            config = self._cam.get_config()
            child = config.get_child_by_name(section).get_child_by_name(option)
            if child.get_type() == gp.GP_WIDGET_RADIO:
                choices = [c for c in child.get_choices()]
            else:
                choices = None
            data_type = type(child.get_value())
            value = data_type(value)  # Cast value
            if choices and value not in choices:
                LOGGER.warning(
                    "Invalid value '%s' for option %s (possible choices: %s), trying to set it anyway", value, option, choices)
            child.set_value(value)
            self._cam.set_config(config)
        except gp.GPhoto2Error as ex:
            LOGGER.error('Unsupported option %s/%s=%s (%s), configure your DSLR manually', section, option, value, ex)

    def get_config_value(self, section, option):
        """Get camera configuration option.
        """
        try:
            config = self._cam.get_config()
            child = config.get_child_by_name(section).get_child_by_name(option)
            value = child.get_value()
            LOGGER.debug('Getting option %s/%s=%s', section, option, value)
            return value
        except gp.GPhoto2Error:
            raise ValueError('Unknown option {}/{}'.format(section, option))

    def preview(self, window, flip=True):
        """Setup the preview.
        """
        self._window = window
        self._preview_hflip = flip

        if self._preview_compatible:
            self.set_config_value('actions', 'viewfinder', 1)
            self._window.show_image(self._get_preview_image())

    def preview_countdown(self, timeout, alpha=80):
        """Show a countdown of `timeout` seconds on the preview.
        Returns when the countdown is finished.
        """
        timeout = int(timeout)
        if timeout < 1:
            raise ValueError("Start time shall be greater than 0")

        shown = False
        first_loop = True
        timer = PoolingTimer(timeout)
        while not timer.is_timeout():
            remaining = int(timer.remaining() + 1)
            if not self._overlay or remaining != timeout:
                # Rebluid overlay only if remaining number has changed
                self._show_overlay(str(remaining), alpha)
                timeout = remaining
                shown = False

            updated_rect = None
            if self._preview_compatible:
                updated_rect = self._window.show_image(self._get_preview_image())
            elif not shown:
                updated_rect = self._window.show_image(self._get_preview_image())
                shown = True  # Do not update dummy preview until next overlay update

            if first_loop:
                timer.start()  # Because first preview capture is longer than others
                first_loop = False

            pygame.event.pump()
            if updated_rect:
                pygame.display.update(updated_rect)

        self._show_overlay(LANGUAGES.get(PiConfigParser.language, LANGUAGES['en']).get('smile_message'), alpha)
        self._window.show_image(self._get_preview_image())

    def preview_wait(self, timeout, alpha=80):
        """Wait the given time.
        """
        timeout = int(timeout)
        if timeout < 1:
            raise ValueError("Start time shall be greater than 0")

        timer = PoolingTimer(timeout)
        if self._preview_compatible:
            while not timer.is_timeout():
                updated_rect = self._window.show_image(self._get_preview_image())
                pygame.event.pump()
                if updated_rect:
                    pygame.display.update(updated_rect)
        else:
            time.sleep(timer.remaining())

        self._show_overlay(LANGUAGES.get(PiConfigParser.language, LANGUAGES['en']).get('smile_message'), alpha)
        self._window.show_image(self._get_preview_image())

    def stop_preview(self):
        """Stop the preview.
        """
        self._hide_overlay()
        self._window = None

    def capture(self, filename, effect=None):
        """Capture a new picture.
        """
        if self._preview_compatible:
            self.set_config_value('actions', 'viewfinder', 0)

        effect = str(effect).lower()
        if effect not in self.IMAGE_EFFECTS:
            raise ValueError("Invalid capture effect '{}' (choose among {})".format(effect, self.IMAGE_EFFECTS))

        self._captures[filename] = (self._cam.capture(gp.GP_CAPTURE_IMAGE), effect)
        time.sleep(0.3)  # Necessary to let the time for the camera to save the image

        self._hide_overlay()  # If stop_preview() has not been called

    def quit(self):
        """Close the camera driver, it's definitive.
        """
        if self._cam:
            self._cam.exit()
