# -*- coding: utf-8 -*-

try:
    import cv2
except ImportError:
    cv2 = None


class CvCameraProxyMock:

    """Fake ``cv2.VideoCapture`` returning always the same frame, read from
    an image file. Reading a still image with ``cv2.VideoCapture`` gives a
    single frame, which is not enough for the preview loop and the capture.
    """

    def __init__(self, filename):
        self.frame = cv2.imread(filename)
        self.props = {}
        self.released = False

    def isOpened(self):
        return not self.released

    def get(self, prop):
        if prop == cv2.CAP_PROP_FRAME_WIDTH:
            return self.frame.shape[1]
        if prop == cv2.CAP_PROP_FRAME_HEIGHT:
            return self.frame.shape[0]
        return self.props.get(prop, 0)

    def set(self, prop, value):
        self.props[prop] = value
        return True

    def read(self):
        return True, self.frame.copy()

    def release(self):
        self.released = True


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
    GP_EVENT_FILE_ADDED = 'file'

    GPhoto2Error = Exception

    def __init__(self, fake_captures):
        self.fake_captures = fake_captures

    def check_result(self, thing):
        return object()

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
        return self.capture_preview()

    def capture_preview(self):
        return GpFileMock(self.fake_captures[0].convert('RGB'))

    def capture(self, flag):
        return GpFileMock()

    def trigger_capture(self):
        pass

    def wait_for_event(self, timeout):
        return (self.GP_EVENT_FILE_ADDED, self.capture(None))

    def init(self):
        pass

    def exit(self):
        pass
