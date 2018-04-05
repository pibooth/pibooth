# -*- coding: utf-8 -*-

import os
import shutil


class PiCamera(object):

    def __init__(self):
        self.preview = None

    def start_preview(self, *args, **kwargs):
        self.preview = True

    def add_overlay(self, *args, **kwargs):
        pass

    def remove_overlay(self, *args, **kwargs):
        pass

    def stop_preview(self, *args, **kwargs):
        self.preview = None

    def capture(self, filename):
        shutil.copy2(os.path.join(os.path.dirname(__file__), 'capture.png'), filename)

    def close(self, *args, **kwargs):
        pass
