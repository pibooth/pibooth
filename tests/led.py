#!/usr/bin/env python

import RPi.GPIO as GPIO
from time import sleep
import atexit

#Variables to change as needed
led_pin = 7  # LED pin

#GPIO setup
GPIO.setmode(GPIO.BOARD)
GPIO.setup(led_pin,GPIO.OUT) # LED 

def cleanup():
  print('Goodbye.')
  GPIO.cleanup()
atexit.register(cleanup) 
  
print('Begin Blinking')
print('Press Ctrl+C to exit')

while True:
	GPIO.output(led_pin,True); 
	sleep(0.5)
	GPIO.output(led_pin,False);
	sleep(0.5)
      
