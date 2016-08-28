#!/usr/bin/env python

import picamera
from time import sleep

camera = picamera.PiCamera()
camera.start_preview()
sleep(3)
camera.capture('image.jpg')
camera.stop_preview()