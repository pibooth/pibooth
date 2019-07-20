# -*- coding: utf-8 -*-

import io
import time
try:
    import gphoto2 as gp
except ImportError:
    gp = None  # gphoto2 is optional
from PIL import Image, ImageFilter
from pibooth.pictures import sizing
from pibooth.controls.camera.rpi import RpiCamera
from pibooth.controls.camera.gphoto import GpCamera


class HybridCamera(RpiCamera):

    """Camera management using the Raspberry Pi camera for the preview (better
    video rendering) and a gPhoto2 compatible camera for the capture (higher
    resolution)
    """

    IMAGE_EFFECTS = GpCamera.IMAGE_EFFECTS

    def __init__(self, *args, **kwargs):
        RpiCamera.__init__(self, *args, **kwargs)
        gp.check_result(gp.use_python_logging())
        self._gp_cam = gp.Camera()
        self._gp_cam.init()

        config = self._gp_cam.get_config()
        gp_set_config_value(config, 'imgsettings', 'iso', self._cam.iso)
        gp_set_config_value(config, 'settings', 'capturetarget', 'Memory card')
        self._gp_cam.set_config(config)

    def _post_process_capture(self, capture_path):
        gp_path, effect = self._captures[capture_path]
        camera_file = gp.check_result(gp.gp_camera_file_get(
            self._gp_cam, gp_path.folder, gp_path.name, gp.GP_FILE_TYPE_NORMAL))

        image = Image.open(io.BytesIO(memoryview(camera_file.get_data_and_size())))
        image = image.crop(sizing.new_size_by_croping_ratio(image.size, self._cam.resolution))

        if self._cam.hflip:
            image = image.transpose(Image.FLIP_LEFT_RIGHT)

        if effect != 'none':
            image = image.filter(getattr(ImageFilter, effect.upper()))

        image.save(capture_path)
        return image

    def capture(self, filename, effect=None):
        """Capture a picture in a file.
        """
        effect = str(effect).lower()
        if effect not in self.IMAGE_EFFECTS:
            raise ValueError("Invalid capture effect '{}' (choose among {})".format(effect, self.IMAGE_EFFECTS))

        self._captures[filename] = (self._gp_cam.capture(gp.GP_CAPTURE_IMAGE), effect)
        time.sleep(1)  # Necessary to let the time for the camera to save the image

        self._hide_overlay()  # If stop_preview() has not been called

    def quit(self):
        """Close the camera driver, it's definitive.
        """
        RpiCamera.quit(self)
        self._gp_cam.exit()
