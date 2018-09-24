# -*- coding: utf-8 -*-

"""
Mocks for tests on other HW than Raspberry Pi.
"""


import os
import time
import shutil


class PiCamera(object):

    IMAGE_EFFECTS = {u'blur': 15,
                     u'cartoon': 22,
                     u'colorbalance': 21,
                     u'colorpoint': 20,
                     u'colorswap': 17,
                     u'deinterlace1': 23,
                     u'deinterlace2': 24,
                     u'denoise': 7,
                     u'emboss': 8,
                     u'film': 14,
                     u'gpen': 11,
                     u'hatch': 10,
                     u'negative': 1,
                     u'none': 0,
                     u'oilpaint': 9,
                     u'pastel': 12,
                     u'posterise': 19,
                     u'saturation': 16,
                     u'sketch': 6,
                     u'solarize': 2,
                     u'washedout': 18,
                     u'watercolor': 13}

    def __init__(self):
        self.preview = None

    def start_preview(self, *args, **kwargs):
        print("Mock: start preview")
        self.preview = True

    def add_overlay(self, *args, **kwargs):
        print("Mock: add overlay")

    def remove_overlay(self, *args, **kwargs):
        print("Mock: remove overlay")

    def stop_preview(self, *args, **kwargs):
        print("Mock: stop preview")
        self.preview = None

    def capture(self, filename):
        print("Mock: capture picture")
        shutil.copy2(os.path.join(os.path.dirname(__file__), 'capture.png'), filename)
        time.sleep(0.5)

    def close(self, *args, **kwargs):
        print("Mock: quit camera")
