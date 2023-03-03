# -*- coding: utf-8 -*-


import io
from PIL import Image


class RpiCameraProxyMock:

    MAX_RESOLUTION = (3280, 2464)

    def __init__(self, fake_captures):
        self.preview = None
        self.fake_captures = fake_captures

    def add_overlay(imagebytes, size, layer=3, window=tuple(), fullscreen=False):
        return object()

    def remove_overlay(self, overlay):
        pass

    def start_preview(self, resolution=tuple(), hflip=False, fullscreen=False, window=tuple()):
        self.preview = object()

    def stop_preview(self):
        self.preview = None

    def capture(self, stream, format='jpeg'):
        im = Image.open(self.fake_captures[0])
        im.save(stream, format=format)

    def close(self):
        pass


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
        return GpConfigMock(name)


class GpFileMock:

    def __init__(self, image=None):
        self.folder = 'fake'
        self.name = 'cam_01.jpg'
        self.image = image
    
    def get_data_and_size(self):
        return self.image


class GpAbilitiesMock:

    operations = 1


class GpCameraProxyMock:

    GP_OPERATION_CAPTURE_PREVIEW = 1
    GP_FILE_TYPE_NORMAL = 'normal'
    GP_CAPTURE_IMAGE = 'capture'
    GP_LOG_VERBOSE = 'verbose'
    GP_WIDGET_RADIO = 'radio'
    
    GPhoto2Error = Exception

    def __init__(self, fake_captures):
        self.fake_captures = fake_captures
        
    def check_result(self, thing):
        return object()

    def gp_log_add_func(self, level, callback):
        pass

    def gp_log_add_func(self, level, callback):
        pass

    def get_abilities(self):
        return GpAbilitiesMock()

    def get_config(self):
        return GpConfigMock()
        
    def set_config(self, config):
        pass

    def file_delete(self, folder, name):
        pass

    def file_get(self, folder, name, flag):
        return GpFileMock(Image.open(self.fake_captures[0]).tobytes("xbm", "rgb"))

    def capture_preview(self):
        return GpFileMock(Image.open(self.fake_captures[0]).tobytes("xbm", "rgb"))

    def capture(self, flag):
        return GpFileMock()

    def exit(self):
        pass
