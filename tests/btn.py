#!/usr/bin/env python

import RPi.GPIO as GPIO
from time import sleep
import atexit

#Variables to change as needed
btn_pin = 18 # pin for the button
debounce = 0.3 # how long to debounce the button. Add more time if the button triggers too many times.

#GPIO setup
GPIO.setmode(GPIO.BOARD)
GPIO.setup(btn_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def cleanup():
  print('Goodbye.')
  GPIO.cleanup()
atexit.register(cleanup) 
	  
print('Push Button')
print('Press Ctrl+C to exit')

while True:
	
	GPIO.wait_for_edge(btn_pin, GPIO.FALLING)
	sleep(debounce)
	print("Button pressed")
      
