# -*- coding: utf-8 -*-

import io
import time
try:
    import gphoto2 as gp
except ImportError:
    gp = None  # gphoto2 is optional
from PIL import Image, ImageFilter
from pibooth.pictures import sizing
from pibooth.utils import LOGGER, pkill
from pibooth.camera.base import BaseCamera


def get_gp_camera_proxy(port=None):
    """Return camera proxy if a gPhoto2 compatible camera is found
    else return None.

    .. note:: try to kill any process using gPhoto2 as it may block camera access.

    :param port: look on given port number
    :type port: str
    """
    if not gp:
        return None  # gPhoto2 is not installed

    pkill('*gphoto2*')
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
        LOGGER.debug("Found gPhoto2 cameras on ports: '%s'", "' / '".join([p for _, p in cameras]))
        # Initialize first camera proxy and return it
        camera = gp.Camera()
        if port is not None:
            port_info_list = gp.PortInfoList()
            port_info_list.load()
            idx = port_info_list.lookup_path(port)
            camera.set_port_info(port_info_list[idx])

        try:
            camera.init()
            return camera
        except gp.GPhoto2Error as ex:
            LOGGER.warning("Could not connect gPhoto2 camera: %s", ex)

    return None


def gp_log_callback(level, domain, string, data=None):
    """Logging callback for gphoto2.
    """
    LOGGER.getChild('gphoto2').debug(domain.decode("utf-8") + u': ' + string.decode("utf-8"))


class GpCamera(BaseCamera):

    """gPhoto2 camera management.
    """

    IMAGE_EFFECTS = ['none',
                     'blur',
                     'contour',
                     'detail',
                     'edge_enhance',
                     'edge_enhance_more',
                     'emboss',
                     'find_edges',
                     'smooth',
                     'smooth_more',
                     'sharpen']

    def __init__(self, camera_proxy):
        super().__init__(camera_proxy)
        self._gp_logcb = None
        self._preview_compatible = True
        self._preview_viewfinder = False

    def _specific_initialization(self):
        """Camera initialization.
        """
        self._gp_logcb = gp.check_result(gp.gp_log_add_func(gp.GP_LOG_VERBOSE, gp_log_callback))
        abilities = self._cam.get_abilities()
        self._preview_compatible = gp.GP_OPERATION_CAPTURE_PREVIEW ==\
            abilities.operations & gp.GP_OPERATION_CAPTURE_PREVIEW
        if not self._preview_compatible:
            LOGGER.warning("The connected DSLR camera is not compatible with preview")
        else:
            try:
                self.get_config_value('actions', 'viewfinder')
                self._preview_viewfinder = True
            except ValueError:
                self._preview_viewfinder = False

        self.set_config_value('imgsettings', 'iso', self.preview_iso)
        self.set_config_value('settings', 'capturetarget', 'Memory card')

    def set_config_value(self, section, option, value):
        """Set camera configuration.
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
                if value == 'Memory card' and 'card' in choices:
                    value = 'card'  # Fix for Sony ZV-1
                elif value == 'Memory card' and 'card+sdram' in choices:
                    value = 'card+sdram'  # Fix for Sony ILCE-6400
                else:
                    LOGGER.warning("Invalid value '%s' for option %s (possible choices: %s), trying to set it anyway",
                                   value, option, choices)
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

    def _rotate_image(self, image, rotation):
        """Rotate a PIL image, same direction than RpiCamera.
        """
        if rotation == 90:
            return image.transpose(Image.ROTATE_90)
        elif rotation == 180:
            return image.transpose(Image.ROTATE_180)
        elif rotation == 270:
            return image.transpose(Image.ROTATE_270)
        return image

    def get_preview_image(self):
        """Capture a new preview image.
        """
        if self._preview_compatible:
            cam_file = self._cam.capture_preview()
            image = Image.open(io.BytesIO(cam_file.get_data_and_size()))
            image = self._rotate_image(image, self.preview_rotation)
            # Crop to keep aspect ratio of the resolution
            image = image.crop(sizing.new_size_by_croping_ratio(image.size, self.resolution))
            # Resize to fit the available space in the window
            image = image.resize(sizing.new_size_keep_aspect_ratio(image.size,
                                 (self._rect.width, self._rect.height), 'outer'))

            if self.preview_flip:
                image = image.transpose(Image.FLIP_LEFT_RIGHT)
        else:
            image = Image.new('RGB', (self._rect.width, self._rect.height), color=(0, 0, 0))
            time.sleep(0.1)

        if self._overlay:
            image.paste(self._overlay, (0, 0), self._overlay)
        return image

    def _process_capture(self, capture_data):
        """Rework capture data.

        :param capture_data: couple (GPhotoPath, effect)
        :type capture_data: tuple
        """
        gp_path, effect = capture_data
        camera_file = self._cam.file_get(gp_path.folder, gp_path.name, gp.GP_FILE_TYPE_NORMAL)
        if self.delete_internal_memory:
            LOGGER.debug("Delete capture '%s' from internal memory", gp_path.name)
            self._cam.file_delete(gp_path.folder, gp_path.name)
        image = camera_file.get_data_and_size()
        if not isinstance(image, Image.Image):  # For unittests
            image = Image.open(io.BytesIO(image))
        image = self._rotate_image(image, self.capture_rotation)

        # Crop to keep aspect ratio of the resolution
        image = image.crop(sizing.new_size_by_croping_ratio(image.size, self.resolution))
        # Resize to fit the resolution
        image = image.resize(sizing.new_size_keep_aspect_ratio(image.size, self.resolution, 'outer'))

        if self.capture_flip:
            image = image.transpose(Image.FLIP_LEFT_RIGHT)

        if effect != 'none':
            image = image.filter(getattr(ImageFilter, effect.upper()))

        return image

    def preview(self, rect, flip=True):
        """Setup the preview.
        """
        if self._preview_compatible:
            if self._preview_viewfinder:
                self.set_config_value('actions', 'viewfinder', 1)
        super().preview(rect, flip)

    def get_capture_image(self, effect=None):
        """Capture a new picture.
        """
        if self._preview_viewfinder:
            self.set_config_value('actions', 'viewfinder', 0)

        if self.capture_iso != self.preview_iso:
            self.set_config_value('imgsettings', 'iso', self.capture_iso)

        self._captures.append((self._cam.capture(gp.GP_CAPTURE_IMAGE), effect))
        time.sleep(0.2)  # Necessary to let the time for the camera to save the image

        if self.capture_iso != self.preview_iso:
            self.set_config_value('imgsettings', 'iso', self.preview_iso)

        return self._captures[-1][0]

    def _specific_cleanup(self):
        """Close the camera driver, it's definitive.
        """
        if self._cam:
            del self._gp_logcb  # Uninstall log callback
            self._cam.exit()
