# -*- coding: utf-8 -*-

import os
import shutil


class PiCamera(object):

    def __init__(self):
        self.preview = None

    def start_preview(self, *args, **kwargs):
        print("Start preview")
        self.preview = True

    def add_overlay(self, *args, **kwargs):
        print("Add overlay")

    def remove_overlay(self, *args, **kwargs):
        print("Remove overlay")

    def stop_preview(self, *args, **kwargs):
        print("Stop preview")
        self.preview = None

    def capture(self, filename):
        print("Capture picture")
        shutil.copy2(os.path.join(os.path.dirname(__file__), 'capture.png'), filename)

    def close(self, *args, **kwargs):
        print("Quit camera")
