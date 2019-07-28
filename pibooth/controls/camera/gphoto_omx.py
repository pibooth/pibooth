# -*- coding: utf-8 -*-

import os
import time
import signal
import subprocess
from PIL import Image
from pibooth.config.parser import PiConfigParser
from pibooth.utils import PoolingTimer
from pibooth.controls.camera.gphoto import gp, GpCamera, LANGUAGES


class GpOmxCamera(GpCamera):

    """gPhoto2 camera management using Omxplayer as preview.
    """

    def __init__(self, *args, **kwargs):
        kwargs['init'] = False
        GpCamera.__init__(self, *args, **kwargs)
        self.gphoto2_process = None
        self.omxplayer_process = None

    def _initialize(self):
        """Camera initialisation
        """
        self._cam = gp.Camera()
        self._cam.init()
        self.set_config_value('imgsettings', 'iso', self._iso)
        self.set_config_value('settings', 'capturetarget', 'Memory card')

    def _show_overlay(self, text, alpha):
        """Add an image as an overlay.
        """
        if self._window:  # No window means no preview displayed
            rect = self._window.get_rect()
            size = (((rect.width + 31) // 32) * 32, ((rect.height + 15) // 16) * 16)

            image = Image.new('RGB', size, color=(0, 0, 0))
            self._overlay = self.build_overlay(image.size, text, alpha)
            image.paste(self._overlay, (0, 0), self._overlay)
            self._window.show_image(image)

    def preview(self, window, flip=True):
        """Setup the preview.
        """
        self._window = window
        self.gphoto2_process = True  # hack to avoid the preview
        if not self.gphoto2_process:
            rect = self.get_rect()
            if flip:
                orientation = 1
            else:
                orientation = 0
            self.gphoto2_process = subprocess.Popen("gphoto2 --capture-movie --stdout> fifo.mjpg &",
                                                    shell=True,
                                                    preexec_fn=os.setsid)
            window_rect = '{0},{1},{2},{3}'.format(tuple(rect)[0], tuple(rect)[1], tuple(rect)[0] + tuple(rect)[2],
                                                   tuple(rect)[1] + tuple(rect)[3])
            command = "omxplayer fifo.mjpg --live --crop 252,0,804,704 --win {0} --orientation {1}".format(
                window_rect, orientation)
            self.omxplayer_process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True, preexec_fn=os.setsid)

    def preview_countdown(self, timeout, alpha=60):
        """Show a countdown of `timeout` seconds on the preview.
        Returns when the countdown is finished.
        """
        timeout = int(timeout)
        if timeout < 1:
            raise ValueError("Start time shall be greater than 0")

        timer = PoolingTimer(timeout)
        while not timer.is_timeout():
            self.preview(self._window)
            remaining = int(timer.remaining() + 1)
            if not self._overlay or remaining != timeout:
                # Rebluid overlay only if remaining number has changed
                self._show_overlay(str(remaining), alpha)
                timeout = remaining

        self._show_overlay(LANGUAGES.get(PiConfigParser.language, LANGUAGES['en']).get('smile_message'), alpha)

    def preview_wait(self, timeout, alpha=60):
        """Wait the given time.
        """
        time.sleep(timeout)
        self._show_overlay(LANGUAGES.get(PiConfigParser.language, LANGUAGES['en']).get('smile_message'), alpha)

    def stop_preview(self):
        """Stop the preview.
        """
        if self.omxplayer_process:
            os.killpg(os.getpgid(self.omxplayer_process.pid), signal.SIGTERM)
            self.omxplayer_process = None
        self._window = None

    def capture(self, filename, effect=None):
        """Capture a picture in a file.
        """
        effect = str(effect).lower()
        if effect not in self.IMAGE_EFFECTS:
            raise ValueError("Invalid capture effect '{}' (choose among {})".format(effect, self.IMAGE_EFFECTS))

        self._initialize()
        self._captures[filename] = (self._cam.capture(gp.GP_CAPTURE_IMAGE), effect)
        time.sleep(1)  # Necessary to let the time for the camera to save the image
        self.quit()

        self._hide_overlay()  # If stop_preview() has not been called
