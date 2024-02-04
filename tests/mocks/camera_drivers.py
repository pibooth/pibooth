# -*- coding: utf-8 -*-

from itertools import cycle
from PIL import ImageOps


class RpiCameraProxyMock:

    MAX_RESOLUTION = (3280, 2464)

    def __init__(self, fake_captures):
        self.preview = None
        self._take = cycle(fake_captures)

    def add_overlay(self, imagebytes, size, layer=3, window=tuple(), fullscreen=False):
        return object()

    def remove_overlay(self, overlay):
        pass

    def start_preview(self, resolution=tuple(), hflip=False, fullscreen=False, window=tuple()):
        self.preview = object()

    def stop_preview(self):
        self.preview = None

    def capture(self, stream, format='jpeg'):
        next(self._take).convert('RGB').save(stream, format=format)

    def close(self):
        pass


class LibcameraCameraProxyMock:

    class Transform:

        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs

    def __init__(self, fake_captures):
        self._take = cycle(fake_captures)
        self.sensor_resolution = fake_captures[0].size
        self.config = None

    def create_preview_configuration(self):
        return {'type': 'preview', 'main': {}}

    def create_still_configuration(self):
        return {'type': 'still', 'main': {'size': self.sensor_resolution}}

    def configure(self, config):
        self.config = config

    def start(self):
        pass

    def stop(self):
        pass

    def capture_image(self, channel):
        return ImageOps.fit(next(self._take), self.config[channel]['size'])

    def switch_mode(self, config):
        self.config = config

    def switch_mode_and_capture_image(self, config, channel):
        old_config = self.config
        self.config = config
        image = self.capture_image(channel)
        self.config = old_config
        return image


class GpCameraProxyMock:

    GP_OPERATION_CAPTURE_PREVIEW = 1
    GP_FILE_TYPE_NORMAL = 'normal'
    GP_CAPTURE_IMAGE = 'capture'
    GP_LOG_VERBOSE = 'verbose'
    GP_WIDGET_RADIO = 'radio'
    GP_EVENT_FILE_ADDED = 'file'

    GPhoto2Error = Exception

    class GpFileMock:

        def __init__(self, image=None):
            self.folder = 'fake'
            self.name = 'cam_01.jpg'
            self.image = image

        def get_data_and_size(self):
            return self.image

    class GpConfigMock:

        def __init__(self, name=""):
            self.name = name

        def get_type(self):
            return int

        def get_value(self):
            return 2

        def get_choices(self):
            return []

        def set_value(self, value):
            pass

        def get_child_by_name(self, name):
            return GpCameraProxyMock.GpConfigMock(name)

    class GpAbilitiesMock:

        operations = 1

    def __init__(self, fake_captures):
        self._take = cycle(fake_captures)

    def check_result(self, thing):
        return object()

    def gp_log_add_func(self, level, callback):
        pass

    def get_abilities(self):
        return GpCameraProxyMock.GpAbilitiesMock()

    def get_config(self):
        return GpCameraProxyMock.GpConfigMock()

    def set_config(self, config):
        pass

    def file_delete(self, folder, name):
        pass

    def file_get(self, folder, name, flag):
        return self.capture_preview()

    def capture_preview(self):
        return GpCameraProxyMock.GpFileMock(next(self._take).convert('RGB'))

    def capture(self, flag):
        return GpCameraProxyMock.GpFileMock(next(self._take).convert('RGB'))

    def trigger_capture(self):
        pass

    def wait_for_event(self, timeout):
        return (self.GP_EVENT_FILE_ADDED, self.capture(None))

    def exit(self):
        pass
