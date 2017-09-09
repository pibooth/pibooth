import RPi.GPIO as GPIO, time, os, subprocess

GPIO.setmode(GPIO.BCM)
switch = 23
ready_led = 17 #button led
busy_led = 24  #red led
pose_led = 18  #blue led
GPIO.setup(switch, GPIO.IN)
GPIO.setup(busy_led, GPIO.OUT)
GPIO.setup(ready_led, GPIO.OUT)
GPIO.setup(pose_led, GPIO.OUT)

GPIO.output(ready_led, False)
GPIO.output(busy_led, 0)
GPIO.output(pose_led, 0)
try:
    GPIO.output(ready_led, 1)
    while (True):
        #print(GPIO.input(switch))
        if (not GPIO.input(switch)):
            #subprocess.call("sudo /home/pi/photobooth/restart_printer", shell=True)
            os.system("sudo service cups restart")
            tick = 0
            while tick < 4:
                #subprocess.call("sudo /home/pi/photobooth/restart_printer", shell=True)
                GPIO.output(ready_led, 0)
                GPIO.output(pose_led, 1)
                print("button pushed, take 4 photos")
                for i in range(5):
                    GPIO.output(pose_led, 0)
                    time.sleep(0.4)
                    GPIO.output(pose_led, 1)
                    time.sleep(0.4)
                for j in range(5):
                    GPIO.output(pose_led, 0)
                    time.sleep(0.1)
                    GPIO.output(pose_led, 1)
                    time.sleep(0.1)
                print("CLICK!")
                #gpout = "OK"
                gpout = subprocess.check_output("gphoto2 --capture-image-and-download --filename /home/pi/photobooth/foto%H%M%S.jpg", stderr=subprocess.STDOUT, shell=True)
                print(gpout)
                if "ERROR" not in gpout:
                    tick += 1
                GPIO.output(pose_led, 0)
                time.sleep(0.5)
            GPIO.output(busy_led, 1)
            print("about to call print_photo script...")
            subprocess.call("sudo /home/pi/photobooth/print_photo", shell=True)
            time.sleep(50)
            subprocess.call("sudo /home/pi/photobooth/restart_printer", shell=True)
            time.sleep(5)
            GPIO.output(busy_led, 0)
            GPIO.output(ready_led, 1)
            GPIO.output(pose_led, 0)
            os.system("sudo reboot")
        #else:
            #print("OFF")
            #GPIO.output(ready_led, 0)
            #GPIO.output(busy_led, 0)
finally:
    GPIO.cleanup()