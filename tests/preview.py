#!/usr/bin/env python
# run the camera preview indefinitely to check physical hardware mounting

import atexit
import picamera
from time import sleep

camera = picamera.PiCamera()
camera.led = False # turn off the LED

def cleanup():
  global camera
  print('Ended abruptly')
  camera.stop_preview() # stop the preview
atexit.register(cleanup)

print "Press ctrl+C to exit"
camera.start_preview() # start the preview

while True:
	sleep(1) # loop until python forced to quit by keyboard