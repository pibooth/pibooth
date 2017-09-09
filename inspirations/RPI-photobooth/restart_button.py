#!/usr/bin/python

import RPi.GPIO as GPIO, time, os, subprocess

GPIO.setmode(GPIO.BCM)
switch = 22
green_led = 25

GPIO.setup(green_led, GPIO.OUT)
GPIO.setup(switch, GPIO.IN)

GPIO.output(green_led, 0)
try:
    GPIO.output(green_led, 1)
    while (True):
        #print(GPIO.input(switch))
        if (not GPIO.input(switch)):
            #print("Button pushed JOOL!")
            GPIO.output(green_led, 0)
            #os.system("sudo python button.py")
            subprocess.call("sudo python /home/pi/photobooth/button.py", shell=True)
            time.sleep(5)
            GPIO.output(green_led, 1)
            time.sleep(1)
        #else:
            #print("OFF")
            #GPIO.output(ready_led, 0)
            #GPIO.output(busy_led, 0)
finally:
    GPIO.cleanup()