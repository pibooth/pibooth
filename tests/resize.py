#!/usr/bin/env python
# Testing image conversion
# Move this file to the main directory (next to config.py) to test

import os
import sys
import socket
import config # this is the config python file config.py

now = "2016-07-31-10-26-26" # run the photobooth at least once, to get a batch of photos in there. Then set this to match their filenames.
total_pics = 4 # number of pics to be taken
gif_delay = 100 # How much time between frames in the animated gif

# gm convert -size 500x500 2016-07-31-10-26-26-01.jpg -thumbnail 500x500 sm.jpg"

for x in range(1, total_pics+1): #batch process all the images
	print x
	graphicsmagick = "gm convert -size 500x500 " + config.file_path + now + "-0" + str(x) + ".jpg -thumbnail 500x500 " + config.file_path + now + "-0" + str(x) + "-sm.jpg"
	os.system(graphicsmagick) #do the graphicsmagick action

graphicsmagick = "gm convert -delay " + str(gif_delay) + " " + config.file_path + now + "*-sm.jpg " + config.file_path + now + ".gif" 
os.system(graphicsmagick) #make the .gif

print "done"