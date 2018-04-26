# -*- coding: utf-8 -*-

"""
Mocks for tests on other HW than Raspberry Pi.
"""


import os
import time
import shutil


class PiCamera(object):

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
