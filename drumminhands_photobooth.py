#!/usr/bin/env python
# created by chris@drumminhands.com
# see instructions at http://www.drumminhands.com/2014/06/15/raspberry-pi-photo-booth/

import os
import time
from time import sleep
import RPi.GPIO as GPIO
import picamera
import atexit
import sys
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage
from email.MIMEBase import MIMEBase
from email import Encoders
import smtplib
import socket
import pygame
from signal import alarm, signal, SIGALRM, SIGKILL

########################
### Variables Config ###
########################
led1_pin = 15 # LED 1
led2_pin = 19 # LED 2
led3_pin = 21 # LED 3
led4_pin = 23 # LED 4
button1_pin = 22 # pin for the big red button
button2_pin = 18 # pin for button to shutdown the pi
button3_pin = 16 # pin for button to end the program, but not shutdown the pi

total_pics = 4 # number of pics  to be taken
capture_delay = 3 # delay between pics
prep_delay = 4 # number of seconds at step 1 as users prep to have photo taken
gif_delay = 100 # How much time between frames in the animated gif

file_path = '/home/pi/photobooth/' #where do you want to save the photos
tumblr_blog = 'username.tumblr.com' # change to your tumblr page
addr_to   = 'secretcodehere@tumblr.com' # The special tumblr auto post email address
addr_from = 'username@gmail.com' # change to your full gmail address
user_name = 'username' # change to your gmail username
password = 'secretpasswordhere' # change to your gmail password
test_server = 'www.google.com'

w = 800 # width of screen in pixels
h = 480 # height of screen in pixels
transform_x = 640 # how wide to scale the jpg when replaying
transfrom_y = 480 # how high to scale the jpg when replaying
offset_x = 80 # how far off to left corner to display photos
offset_y = 0 # how far off to left corner to display photos
replay_delay = 1 # how much to wait in-between showing pics on-screen after taking
replay_cycles = 4 # how many times to show each photo on-screen after taking

####################
### Other Config ###
####################
GPIO.setmode(GPIO.BOARD)
GPIO.setup(led1_pin,GPIO.OUT) # LED 1
GPIO.setup(led2_pin,GPIO.OUT) # LED 2
GPIO.setup(led3_pin,GPIO.OUT) # LED 3
GPIO.setup(led4_pin,GPIO.OUT) # LED 4
GPIO.setup(button1_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP) # falling edge detection on button 1
GPIO.setup(button2_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP) # falling edge detection on button 2
GPIO.setup(button3_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP) # falling edge detection on button 3
GPIO.output(led1_pin,False);
GPIO.output(led2_pin,False);
GPIO.output(led3_pin,False);
GPIO.output(led4_pin,False); #for some reason the pin turns on at the beginning of the program. why?????????????????????????????????

#################
### Functions ###
#################

def cleanup():
  print('Ended abruptly')
  GPIO.cleanup()
atexit.register(cleanup)

def shut_it_down(channel):  
    print "Shutting down..." 
    GPIO.output(led1_pin,True);
    GPIO.output(led2_pin,True);
    GPIO.output(led3_pin,True);
    GPIO.output(led4_pin,True);
    time.sleep(3)
    os.system("sudo halt")

def exit_photobooth(channel):
    print "Photo booth app ended. RPi still running" 
    GPIO.output(led1_pin,True);
    time.sleep(3)
    sys.exit()
    
def is_connected():
  try:
    # see if we can resolve the host name -- tells us if there is
    # a DNS listening
    host = socket.gethostbyname(test_server)
    # connect to the host -- tells us if the host is actually
    # reachable
    s = socket.create_connection((host, 80), 2)
    return True
  except:
     pass
  return False    

def display_pics(jpg_group):
    # this section is an unbelievable nasty hack - for some reason Pygame
    # needs a keyboardinterrupt to initialise in some limited circs (second time running)
    class Alarm(Exception):
        pass
    def alarm_handler(signum, frame):
        raise Alarm
    signal(SIGALRM, alarm_handler)
    alarm(3)
    try:
        pygame.init()
        screen = pygame.display.set_mode((w,h),pygame.FULLSCREEN) 
        alarm(0)
    except Alarm:
        raise KeyboardInterrupt
    pygame.display.set_caption('Photo Booth Pics')
    pygame.mouse.set_visible(False) #hide the mouse cursor	
    for i in range(0, replay_cycles): #show pics a few times
		for i in range(1, total_pics+1): #show each pic
			filename = file_path + jpg_group + "-0" + str(i) + ".jpg"
			img=pygame.image.load(filename) 
			img = pygame.transform.scale(img,(transform_x,transfrom_y))
			screen.blit(img,(offset_x,offset_y))
			pygame.display.flip() # update the display
			time.sleep(replay_delay) # pause 
			
# define the photo taking function for when the big button is pressed 
def start_photobooth(): 
	################################# Begin Step 1 ################################# 
	print "Get Ready" 
	camera = picamera.PiCamera()
	camera.resolution = (500, 375) #use a smaller size to process faster, and tumblr will only take up to 500 pixels wide for animated gifs
	camera.vflip = True
	camera.hflip = True
	camera.saturation = -100
	camera.start_preview()
	i=1 #iterate the blink of the light in prep, also gives a little time for the camera to warm up
	while i < prep_delay :
	  GPIO.output(led1_pin,True); sleep(.5) 
	  GPIO.output(led1_pin,False); sleep(.5); i+=1
	################################# Begin Step 2 #################################
	print "Taking pics" 
	now = time.strftime("%Y%m%d%H%M%S") #get the current date and time for the start of the filename
	try: #take the photos
		for i, filename in enumerate(camera.capture_continuous(file_path + now + '-' + '{counter:02d}.jpg')):
			GPIO.output(led2_pin,True) #turn on the LED
			print(filename)
			sleep(0.25) #pause the LED on for just a bit
			GPIO.output(led2_pin,False) #turn off the LED
			sleep(capture_delay) # pause in-between shots
			if i == total_pics-1:
				break
	finally:
		camera.stop_preview()
		camera.close()
	########################### Begin Step 3 #################################
	print "Creating an animated gif" 
	GPIO.output(led3_pin,True) #turn on the LED
	graphicsmagick = "gm convert -delay " + str(gif_delay) + " " + file_path + now + "*.jpg " + file_path + now + ".gif" 
	os.system(graphicsmagick) #make the .gif
	print "Uploading to tumblr. Please check " + tumblr_blog + " soon." 
	connected = is_connected() #check to see if you have an internet connection
	while connected: 
		try:
			msg = MIMEMultipart()
			msg['Subject'] = now
			msg['From'] = addr_from
			msg['To'] = addr_to
			file_to_upload = file_path + now + ".gif"
			fp = open(file_to_upload, 'rb')
			part = MIMEBase('image', 'gif')
			part.set_payload( fp.read() )
			Encoders.encode_base64(part)
			part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(file_to_upload))
			fp.close()
			msg.attach(part)
			server = smtplib.SMTP('smtp.gmail.com:587')
			server.starttls()
			server.login(user_name, password)
			server.sendmail(msg['From'], msg['To'], msg.as_string())
			server.quit()
			break
		except ValueError:
			print "Oops. No internect connection. Upload later."
			try: #make a text file as a note to upload the .gif later
				file = open(file_path + now + "-FILENOTUPLOADED.txt",'w')   # Trying to create a new file or open one
				file.close()
			except:
				print('Something went wrong. Could not write file.')
				sys.exit(0) # quit Python
	GPIO.output(led3_pin,False) #turn off the LED
	########################### Begin Step 4 #################################
	GPIO.output(led4_pin,True) #turn on the LED
	try:
		display_pics(now)
	except Exception, e:
		tb = sys.exc_info()[2]
		traceback.print_exception(e.__class__, e, tb)
	pygame.quit()
	print "Done"
	GPIO.output(led4_pin,False) #turn off the LED

####################
### Main Program ###
####################

# when a falling edge is detected on button2_pin and button3_pin, regardless of whatever   
# else is happening in the program, their function will be run   
GPIO.add_event_detect(button2_pin, GPIO.FALLING, callback=shut_it_down, bouncetime=300) 
GPIO.add_event_detect(button3_pin, GPIO.FALLING, callback=exit_photobooth, bouncetime=300)  

print "Photo booth app running..." 
GPIO.output(led1_pin,True); #light up the lights to show the app is running at the beginning
GPIO.output(led2_pin,True);
GPIO.output(led3_pin,True);
GPIO.output(led4_pin,True);
time.sleep(3)
GPIO.output(led1_pin,False); #turn off the lights
GPIO.output(led2_pin,False);
GPIO.output(led3_pin,False);
GPIO.output(led4_pin,False);

# wait for the big button to be pressed
while True:
	GPIO.wait_for_edge(button1_pin, GPIO.FALLING)
	time.sleep(0.2) #debounce
	start_photobooth()
