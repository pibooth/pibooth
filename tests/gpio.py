#!/usr/bin/env python

import RPi.GPIO as GPIO
from time import sleep
import atexit

#Variables to change as needed
led_pin = 7    # LED pin
btn_pin = 18   # pin for the button
debounce = 0.3 # how long to debounce the button. Add more time if the button triggers too many times.

#GPIO setup
GPIO.setmode(GPIO.BOARD)
GPIO.setup(led_pin,GPIO.OUT) # LED 
GPIO.setup(btn_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP) # button


def cleanup():
  print('Goodbye.')
  GPIO.cleanup()
atexit.register(cleanup) 

run_state = False

def check_light():
	if run_state:
		GPIO.output(led_pin,True)
		print("LED on")
	else:
		GPIO.output(led_pin,False)
		print("LED off")
		
print('Push Button')
print('Press Ctrl+C to exit')

try:	
	while True:
		GPIO.wait_for_edge(btn_pin, GPIO.FALLING)
		sleep(debounce)
		if run_state:
			run_state = False
		else:
			run_state = True
		print("Button pressed")
		check_light()
except KeyboardInterrupt:
	print('\nScript Exited.')