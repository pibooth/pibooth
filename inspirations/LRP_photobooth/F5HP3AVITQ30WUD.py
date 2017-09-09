#!/usr/bin/X11/python3.4

from tkinter import *
#from tkinter.ttk import *
from tkinter import font, ttk
import RPi.GPIO as GPIO
import subprocess, time, os, shelve 
from tkinter import filedialog
from picamera import PiCamera
from PIL import Image

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
#define GPIO / pins
AMBIENT_LED = 24 
PRINT_LED = 22
POSE_LED = 18
READY_LED = 23
#set up pins
GPIO.setup(AMBIENT_LED, GPIO.OUT)
GPIO.setup(PRINT_LED, GPIO.OUT)
GPIO.setup(POSE_LED, GPIO.OUT)
GPIO.setup(READY_LED, GPIO.OUT)

GPIO.output(AMBIENT_LED, True)
GPIO.output(PRINT_LED, True)
GPIO.output(POSE_LED, True)
GPIO.output(READY_LED, False)

#variables
root = Tk()
ttk.Style().configure("TButton", padding=5, font='helvetica 24', foreground="red", background="white", relief="raised", borderwidth=5)
ttk.Style().configure("TEntry", padding=5, font='helvetica 24', borderwidth=5)
ttk.Style().configure("TLabel", padding=1)
myFont = font.Font(family = "Helvetica", size = 28, weight = "bold")
mytextFont = font.Font(family = "Helvetica", size = 20, weight = "bold")
g_name = "Tell us your name"
g_email = "youraddress@mail.com"
thumb_image=PhotoImage()
sound_check = BooleanVar()
blog_check  = BooleanVar()
email_check = BooleanVar()
print_check = BooleanVar()
admin_check = BooleanVar()
bandg_check = BooleanVar()
num_print_copies = IntVar()
msg = StringVar()
g_event = StringVar()
g_company = StringVar()
g_blog_email = StringVar()
bandg_imgname = StringVar

#set up two cameras
camera = PiCamera()
camera.resolution = (800, 1024)
camera.hflip = False
camera.vflip = False

#GPIO.output(AMBIENT_LED, False)

#define functions
def write_the_shelve():
	shelve_registry = shelve.open('/home/pi/GUI/PB_shelf', writeback=True)
	global blog_check
	global email_check
	global print_check
	global g_event
	global g_company
	global g_blog_email
	global num_print_copies
	global admin_check
	global sound_check
	global bandg_check
	try:
		shelve_registry['post']={'blog':blog_check.get(), 'email':email_check.get(), 'printer':print_check.get(), 'event':g_event.get(), 'company':g_company.get(), 'blog_email':g_blog_email.get(), 'numcopies':num_print_copies.get(), 'admin': admin_check.get(), 'sound': sound_check.get(), 'bandg': bandg_check.get()}
	finally:
		shelve_registry.close()

def read_the_shelve():
	shelve_registry = shelve.open('/home/pi/GUI/PB_shelf')
	
	global blog_check
	global email_check
	global print_check
	global g_event
	global g_company
	global g_blog_email
	global num_print_copies
	global admin_check
	global sound_check
	global bandg_check
	global saved
	try:
		saved =( shelve_registry['post'])
		blog_check.set( saved['blog'])
		email_check.set( saved['email'])
		print_check.set( saved['printer'])
		g_event.set( saved['event'])
		g_company.set( saved['company'])
		g_blog_email.set( saved['blog_email'])
		num_print_copies.set( saved['numcopies'])
		admin_check.set( saved['admin'] )
		sound_check.set( saved['sound'] )
		bandg_check.set( saved['bandg'] )
	finally:
		shelve_registry.close()
def clean_house():
	newfolder = "/home/pi/PB_archive/"+time.strftime("%y%m%d%H%M")
	call ="mkdir "+newfolder
	subprocess.Popen([call], shell=True)
	wait_sec(1, "Moving image files")
	movecall="mv /home/pi/GUI/Images/*.jpg "+newfolder
	subprocess.Popen([movecall], shell=True)
	wait_sec(1, "Moving picture files")
	movecall="mv /home/pi/Pictures/*.jpg "+newfolder
	subprocess.Popen([movecall], shell=True)

def play_sound(sound):
	global sound_check
	if sound_check.get():
		if sound=="click":
			call = "mpg321 button-16.mp3 -q"
			subprocess.call([call], shell=True)
		if sound=="shutter":
			call = "mpg321 camera-shutter-click-07.mp3 -q"
			subprocess.call([call], shell=True)

def progress(perc):
	root_progressbar['value']=perc
	root.update()

def wait_sec(wait_time, message):
	global admin_check
	if admin_check.get()== False:
		message=""
	progress(100)
	divider=wait_time
	for i in range(wait_time):
		if i > 0:
			msg.set(message)
			progress(100-(i*divider))
		else:
			progress(0) 
		GPIO.output(PRINT_LED, FALSE) #this got so annoying it clicked so much that no one ever knew what was going on
		time.sleep(.4)
		GPIO.output(PRINT_LED, TRUE)
		time.sleep(.3)
	GPIO.output(PRINT_LED, True)
	msg.set("")
	progress(0)

def aboutPage():
        subprocess.Popen(["x-www-browser file:///home/pi/GUI/About/About.htm"], shell=True)
def editPrinter():
	subprocess.Popen(["x-www-browser http://127.0.0.1:631"], shell=True)
def editEmail():
	subprocess.Popen(["leafpad /home/pi/.muttrc"], shell=True)
def adminbox():
	adminBox=Toplevel(root)
	CameraStartButton=ttk.Button(adminBox, text="Start Camera", command = camera.start_preview)
	CameraStartButton.grid(column=1, row=1)
	CameraStopButton=ttk.Button(adminBox, text="Stop Camera", command = camera.stop_preview)
	CameraStopButton.grid(column=1, row=2)
	CancelButton=ttk.Button(adminBox, text="Done", command = adminBox.destroy)
	CancelButton.grid(column=1, row=3)

def getready():
	w = root.winfo_screenwidth()/2 # width for the Tk
	h = root.winfo_screenheight()-100 # height for the Tk
	PoseBox=Toplevel(root)
	# get screen width and height
	ws = root.winfo_screenwidth() # width of the screen
	hs = root.winfo_screenheight() # height of the screen
	# calculate x and y coordinates for the Tk root window
	x = (ws/2) - (w/2)
	y = (hs/2) - (h/2)

	PoseBox.geometry('%dx%d+%d+%d' % (w, h, x, y))
	PoseBox.title("Leave the Bride and Groom a Message!")
	PosePic=PhotoImage(file="/home/pi/GUI/Example/bandg.gif")
	imageFrame=ttk.Frame(PoseBox, padding="12 12 12 12", borderwidth=12)
	imageFrame.grid(column=1, row=1)

	imagelabel=ttk.Label(imageFrame, image = PosePic)
	imagelabel.image=PosePic
	imagelabel.grid(column=1, row=1)

	newfile="/home/pi/GUI/Example/bandg.gif"
	PosePic=PhotoImage(file=newfile)
	imagelabel['image']=PosePic
	imagelabel.image=PosePic

	wait_sec(10,"")
	for i in range(9, 0, -1):
		newfile="/home/pi/GUI/Example/"+str(i+1)+".gif"
		PosePic=PhotoImage(file=newfile)
		imagelabel['image']=PosePic
		imagelabel.image=PosePic
		newfile="/home/pi/GUI/Example/"+str(i)+".gif"
		PosePic=PhotoImage(file=newfile)
		imagelabel['image']=PosePic
		imagelabel.image=PosePic
		wait_sec(3, "")

	PoseBox.destroy()
	camera.resolution = (1600, 1024)

	camera.start_preview()
	for i in range(4):
		GPIO.output(POSE_LED, False)
		time.sleep(.4)
		GPIO.output(POSE_LED, True)
		time.sleep(.3)
	for i in range(4):
		GPIO.output(POSE_LED, False)
		time.sleep(.1)
		GPIO.output(POSE_LED, True)
		time.sleep(.1)
	GPIO.output(POSE_LED, True)
	play_sound("shutter")
	bandg_imgname = time.strftime("%Y%m%d%H%M%S")
	camera.capture("/home/pi/Pictures/"+bandg_imgname+".jpg")
	camera.stop_preview()
	call = "montage -tile 1x3 -geometry +5+5 /home/pi/GUI/Example/header.jpg /home/pi/Pictures/"+bandg_imgname+".jpg /home/pi/GUI/Example/footer.jpg /home/pi/Pictures/"+bandg_imgname+".jpg"
	subprocess.call([call], shell=True)
	wait_sec(3, "Finish camera processing.")
	return bandg_imgname

def editPostDialog():

	def savePostDialog():
		ending_text = textbox.get("1.0","end-1c")
		text_file = open("/home/pi/GUI/PostText.txt", "w")
		text_file.write(ending_text)
		text_file.close()
		PostBox.destroy()
		return
	w = 1200 # width for the Tk
	h = 750 # height for the Tk
	PostBox=Toplevel(root)
	# get screen width and height
	ws = root.winfo_screenwidth() # width of the screen
	hs = root.winfo_screenheight() # height of the screen
	# calculate x and y coordinates for the Tk root window
	x = (ws/2) - (w/2)
	y = (hs/2) - (h/2)

	PostBox.geometry('%dx%d+%d+%d' % (w, h, x, y))
	PostBox.title("Update Post Text")

	PostLabel=ttk.Label(PostBox, padding="15 15 15 15", font=myFont, text="E-mail and Blog Text:")
	PostLabel.grid(row=1, column=1, columnspan=4, sticky=W)

	textbox = Text(PostBox)
	textbox.grid(column=1, row=2, columnspan=4, sticky=[E,W])

	ttk.Separator(PostBox,orient=HORIZONTAL).grid(row=3, column=1, ipady=5, columnspan=4, sticky=[E,W])

	BlogmailLabel=ttk.Label(PostBox, padding="15 15 15 15", font=myFont, text="Blog-post address:")
	BlogmailLabel.grid(row=4, column=1)
	emailBox=ttk.Entry(PostBox, textvariable= g_blog_email, font=myFont, width = 35)
	emailBox.grid(column=2, row=4, columnspan =2)

	ttk.Separator(PostBox,orient=HORIZONTAL).grid(row=5, column=1, ipady=5, columnspan=4, sticky=[E,W])

	CancelButton=ttk.Button(PostBox, text="Cancel", command = PostBox.destroy)
	CancelButton.grid(column=2, row=6, sticky=SW)

	DoneButton=ttk.Button(PostBox, text="Done", command = savePostDialog)
	DoneButton.grid(column=3, row=6, sticky=SW)
	
	
	with open('/home/pi/GUI/PostText.txt', 'r') as input_file:
		my_text=input_file.read()
		textbox.insert("end", my_text)

def TakePicture():
	global bandg_check
	global bandg_imgname
	#fix the camera resolution to take portrait photos
	camera.resolution = (800, 1024)
	GPIO.output(READY_LED, True) #not ready
	#play a cool camera sound
	play_sound("click")
	#this will be the montage name; it only goes to the minute
	l_montageName = time.strftime("%Y-%m-%d_%H-%M")

	w = root.winfo_screenwidth()/2 # width for the Tk
	h = root.winfo_screenheight()-150 # height for the Tk
	PoseBox=Toplevel(root)
	# get screen width and height
	ws = root.winfo_screenwidth() # width of the screen
	hs = root.winfo_screenheight() # height of the screen
	# calculate x and y coordinates for the Tk root window
	x = (ws/2) - (w/2)
	y = (hs/2) - (h/2)

	PoseBox.geometry('%dx%d+%d+%d' % (w, h, x, y))
	PoseBox.title("Get Ready!")
	PosePic=PhotoImage(file="/home/pi/GUI/Example/prop.gif")
	imageFrame=ttk.Frame(PoseBox, padding="12 12 12 12", borderwidth=12)
	imageFrame.grid(column=1, row=1)

	imagelabel=ttk.Label(imageFrame, image = PosePic)
	imagelabel.image=PosePic
	imagelabel.grid(column=1, row=1)
	wait_sec(5,"Get a Prop")
	for i in range(9, 0, -1):
		newfile="/home/pi/GUI/Example/"+str(i+1)+".gif"
		PosePic=PhotoImage(file=newfile)
		imagelabel['image']=PosePic
		imagelabel.image=PosePic
		newfile="/home/pi/GUI/Example/"+str(i)+".gif"
		PosePic=PhotoImage(file=newfile)
		imagelabel['image']=PosePic
		imagelabel.image=PosePic
		wait_sec(2, "")
	newfile="/home/pi/GUI/Example/pose.gif"
	PosePic=PhotoImage(file=newfile)
	imagelabel['image']=PosePic
	imagelabel.image=PosePic
	wait_sec(4,"Pose Now")
	PoseBox.destroy()
	snaponePhoto('TL', time.strftime("%Y%m%d%H%M%S"))
	update_TL()
	snaponePhoto('BL', time.strftime("%Y%m%d%H%M%S"))
	update_BL()
	snaponePhoto('TR', time.strftime("%Y%m%d%H%M%S"))
	update_TR()
	snaponePhoto('BR', time.strftime("%Y%m%d%H%M%S"))
	update_BR()

	#build the montage
	wait_sec(4, "Adding your photos to the Montage")	
	call = "montage -tile 2x2 -geometry +5+5 *.jpg "+l_montageName+".jpg"
	subprocess.call([call], shell=True)
	wait_sec(5, "Adding a header and footer to the Montage")
	call = "montage -tile 1x3 -geometry +5+5 /home/pi/GUI/Example/header.jpg "+l_montageName+".jpg /home/pi/GUI/Example/footer.jpg /home/pi/GUI/"+l_montageName+".jpg"
	subprocess.call([call], shell=True)
	wait_sec(5, "And finally, the left and right borders")
	call = "montage -tile 3x1 -geometry +0+0 /home/pi/GUI/Example/RightBorder.gif /home/pi/GUI/"+l_montageName+".jpg /home/pi/GUI/Example/LeftBorder.gif /home/pi/Pictures/"+l_montageName+".jpg"
	subprocess.call([call], shell=True)
	#clean house
	call1="mv /home/pi/GUI/*.jpg /home/pi/GUI/Images/"
	subprocess.Popen([call1], shell=True)
	wait_sec(4, "Making thumbnail photos")
	imagecall2 = "convert -resize 30% /home/pi/Pictures/"+l_montageName+".jpg  /home/pi/GUI/Example/thumb.gif"
	subprocess.Popen([imagecall2], shell=True)
	if bandg_check.get():
		bandg_imgname = getready()	
	sendorDelete(l_montageName)	

def update_TL():
	swapTL=PhotoImage(file="TL.gif")
	topleft['image']=swapTL
	topleft.image=swapTL
	root.update()
def update_TR():
	swapTR=PhotoImage(file="TR.gif")
	topright['image']=swapTR
	topright.image=swapTR
	root.update()
def update_BL():
	swapBL=PhotoImage(file="BL.gif")
	bottomleft['image']=swapBL
	bottomleft.image=swapBL
	root.update()
def update_BR():
	swapBR=PhotoImage(file="BR.gif")
	bottomright['image']=swapBR
	bottomright.image=swapBR
	root.update()

def snaponePhoto(photoName, Timestamp):
	msg.set(photoName)
	camera.start_preview()
	for i in range(4):
		GPIO.output(POSE_LED, False)
		time.sleep(.4)
		GPIO.output(POSE_LED, True)
		time.sleep(.3)
	for i in range(4):
                GPIO.output(POSE_LED, False)
                time.sleep(.1)
                GPIO.output(POSE_LED, True)
                time.sleep(.1)		
	GPIO.output(POSE_LED, True)
	play_sound("shutter")
	camera.capture("/home/pi/GUI/"+Timestamp+".jpg")
	camera.stop_preview()
	wait_sec(3, "Finish camera processing.")
	imagecall="convert -resize 45% /home/pi/GUI/"+Timestamp+".jpg /home/pi/GUI/"+photoName+".gif"
	subprocess.Popen([imagecall], shell=True)
	wait_sec(3, "Resizing photos for thumbnails")

def create_thumb(photoName):
	imagecall="convert "+photoName+".jpg -resize 30% "+photoName+".gif"
	subprocess.Popen([imagecall], shell=True)
	wait_sec(3, "Creating Additional Thumbs") 	

def create_images(action, imagecall):
	wait_sec(action, 5) 
	subprocess.Popen([imagecall], shell=True)

def send(l_name, l_email, l_photoName):
	msg.set("Sending and printing your photos")	
	GPIO.output(PRINT_LED, False)
	global g_blog_email
	global num_print_copies
	subject = 'Hello from Lininger~Rood Photography'

	if email_check.get():
		#send the photo to email
		mutt =  "mutt -s '"+subject+"' "+l_email.get()+"  < /home/pi/GUI/PostText.txt -a /home/pi/Pictures/"+l_photoName+".jpg"
		ml = subprocess.Popen([mutt], shell = True)
		ml.communicate()
	if blog_check.get():
		#post to the blog
		mutt =  "mutt -s '"+subject+"' "+g_blog_email.get()+" < /home/pi/GUI/PostText.txt -a /home/pi/Pictures/"+l_photoName+".jpg"
		ml = subprocess.Popen([mutt], shell = True)
		ml.communicate()
	if print_check.get():
		#print the photo to the local printer
		for i in range(num_print_copies.get()):
			printer = "lp /home/pi/Pictures/"+l_photoName+".jpg"
			subprocess.Popen([printer], shell = True)
			wait_sec(90, "Printing Copies, this takes a minute or two") 
		if bandg_check.get():
			printer = "lp /home/pi/Pictures/"+bandg_imgname+".jpg"
			subprocess.Popen([printer], shell = True)
	wait_sec(5, "Only a few more seconds")
	GPIO.output(PRINT_LED, True)
	GPIO.output(READY_LED, False)

def sendorDelete(l_photoName):
	msg.set("Create Send or Delete Box")
	global myFont
	l_name = StringVar()
	l_name.set(g_name)
	l_email = StringVar()
	l_email.set(g_email)
	photoName = l_photoName

	def sendButtonAction():
		contactBox.destroy()
		play_sound("click")
		fix_swap()
		send(l_name, l_email, photoName)
		msg.set("Ready")
	def deleteButtonAction():
		play_sound("click")
		fix_swap()
		contactBox.destroy()
		GPIO.output(READY_LED, False)
		msg.set("Deleted")

	wait_sec(5, "Preparing your image to display")
	thumb_image=PhotoImage(file="/home/pi/GUI/Example/thumb.gif")
	w = 900 # width for the Tk
	h = 950 # height for the Tk
	contactBox=Toplevel(root)
	# get screen width and height
	ws = root.winfo_screenwidth() # width of the screen
	hs = root.winfo_screenheight() # height of the screen

	# calculate x and y coordinates for the Tk root window
	x = (ws/2) - (w/2)
	y = (hs/2) - (h/2)

	contactBox.geometry('%dx%d+%d+%d' % (w, h, x, y))
	contactFrame=ttk.Frame(contactBox, padding="12 12 12 12")
	imageFrame=ttk.Frame(contactFrame, padding="12 12 12 12", borderwidth=12, relief='sunken')
	imageFrame.grid(column=1, row=3, rowspan=2, columnspan=2)

	imagelabel=ttk.Label(imageFrame, image = thumb_image, padding="12 12 12 12")
	imagelabel.image=thumb_image
	imagelabel.grid(column=1, row=1)



	contactBox.title("Enter Your Contact Info")
	contactFrame.grid(column=0, row=0, sticky=(N, W, E, S))	

	emailBox=ttk.Entry(contactFrame, textvariable= l_email, font=mytextFont, width = 40)
	emailBox.grid(column=2, row=2, columnspan =2)
	ttk.Label(contactFrame, text="Let Us Send Your Memory To You!", font=myFont).grid(column=1, row=1, columnspan=3)
	ttk.Label(contactFrame, text="Your e-Mail:", font= myFont).grid(column=1, row=2, sticky=S)
	
	sendButton=ttk.Button(contactFrame, text="This is It!", command = sendButtonAction)
	sendButton.grid(column=3, row=3)
	deleteButton=ttk.Button(contactFrame, text="Try Again", command = deleteButtonAction)
	deleteButton.grid(column=3, row=4)

	#make this box modal because user will click outside the box, hiding it, and destroying the sequence flow
	emailBox.focus_set()
	contactBox.transient(root)
	contactBox.grab_set()
	root.wait_window(contactBox)

	for child in contactFrame.winfo_children():child.grid_configure(padx=15, pady=5)

def SetUpEvent():
	def write_newEvent_details():
		date=time.strftime("%B %d, %Y")
		call="convert -size 1600x  -font URW-Chancery-L-Medium-Italic -fill red -gravity center label:'"+g_event.get()+"' /home/pi/GUI/Example/header.jpg"
		subprocess.Popen([call], shell = True)
		wait_sec(4, "Making the Event Header")
		call1="convert -size 1600x176 -font URW-Chancery-L-Medium-Italic -pointsize 90 -fill red -gravity center label:'"+date+"'  /home/pi/GUI/Example/footer.jpg"
		subprocess.Popen([call1], shell=True)
		wait_sec(4, "Making the Event Footer")
		call1="convert -size 2245x60 -font URW-Chancery-L-Medium-Italic -pointsize 50 -fill red -gravity Center label:'"+g_company.get()+"' /home/pi/GUI/Example/border.gif"
		subprocess.Popen([call1], shell=True)
		wait_sec(4, "Making the Company Borders")
		call="convert /home/pi/GUI/Example/border.gif -resize 450x25^ -gravity Center -crop 450x25+0+0 +repage /home/pi/GUI/Example/borderthumb.gif"
		subprocess.Popen([call], shell=True)
		call1="convert -rotate 90 /home/pi/GUI/Example/border.gif /home/pi/GUI/Example/RightBorder.gif"
		subprocess.Popen([call1], shell=True)
		call1="convert -rotate 270 /home/pi/GUI/Example/border.gif /home/pi/GUI/Example/LeftBorder.gif"
		subprocess.Popen([call1], shell=True)
		create_thumb("/home/pi/GUI/Example/header")
		header_img=PhotoImage(file="/home/pi/GUI/Example/header.gif")
		time.sleep(.5)
		headerlabel['image']=header_img
		headerlabel.image=header_img
		create_thumb("/home/pi/GUI/Example/footer")
		footer_img=PhotoImage(file="/home/pi/GUI/Example/footer.gif")
		time.sleep(.5)
		footerlabel['image']=footer_img
		footerlabel.image=footer_img	
		border_img=PhotoImage(file="/home/pi/GUI/Example/borderthumb.gif")
		borderlabel['image']=border_img
		borderlabel.image=border_img	
	global g_event
	global g_company
	w = 900 # width for the Tk
	h = 400 # height for the Tk
	EventBox=Toplevel(root)
	# get screen width and height
	ws = root.winfo_screenwidth() # width of the screen
	hs = root.winfo_screenheight() # height of the screen
	# calculate x and y coordinates for the Tk root window
	x = (ws/2) - (w/2)
	y = (hs/2) - (h/2)
	
	EventBox.geometry('%dx%d+%d+%d' % (w, h, x, y))
	EventFrame=ttk.Frame(EventBox, padding="12 12 12 12")
	EventBox.title("Update Event Details")
	ttk.Label(EventFrame, text="Host Name:", font=myFont).grid(column=1, row=1, sticky = W)
	CompanyEntryBox=ttk.Entry(EventFrame, textvariable= g_company, font=mytextFont, width = 40)
	CompanyEntryBox.grid(column=2, row=1, columnspan =2, sticky = [E,W])
	ttk.Label(EventFrame, text="Event Name:", font= myFont).grid(column=1, row=2, sticky = W)
	EventEntryBox=ttk.Entry(EventFrame, textvariable= g_event, font=mytextFont, width = 40)
	EventEntryBox.grid(column=2, row=2, columnspan =2, sticky = [E,W])
	ttk.Separator(EventFrame,orient=HORIZONTAL).grid(row=3, columnspan=4, sticky=[E,W])
	LabelBox=ttk.Frame(EventFrame, padding="15 15 12 12", borderwidth=10, relief='sunken')
	LabelBox.grid(column=1, row=5, columnspan=3)
	header_img=PhotoImage(file="/home/pi/GUI/Example/header.gif")
	headerlabel=ttk.Label(LabelBox, image = header_img)
	headerlabel.image=header_img
	headerlabel.grid(column=1, row=2, columnspan=3)
	footer_img=PhotoImage(file="/home/pi/GUI/Example/footer.gif")
	footerlabel=ttk.Label(LabelBox, image = footer_img)
	footerlabel.image=footer_img
	footerlabel.grid(column=1, row=3, columnspan=3)
	border_img=PhotoImage(file="/home/pi/GUI/Example/borderthumb.gif")
	borderlabel=ttk.Label(LabelBox, image = border_img)
	borderlabel.image=border_img
	borderlabel.grid(column=1, row=1, columnspan=3)
	ttk.Separator(EventFrame,orient=HORIZONTAL).grid(row=7, columnspan=4, stick=[E,W])
	
	ttk.Label(EventFrame, text="Number of Prints").grid(column=1, row=8)
	numprintEntry=Spinbox(EventFrame, from_=1, to=2, textvariable=num_print_copies)
	numprintEntry.grid(column=1, row=9)
	EventUpdateButton=ttk.Button(EventFrame, text="Create New Image Label", command = write_newEvent_details)
	EventUpdateButton.grid(column=2, row=8, rowspan=2)
	EventDoneButton=ttk.Button(EventFrame, text="Done", command = EventBox.destroy)
	EventDoneButton.grid(column=3, row=8, rowspan=2, stick = E)

	for child in EventBox.winfo_children():child.grid_configure(padx=10, pady=20)

def exitProgram():
	write_the_shelve()
	GPIO.cleanup()
	root.destroy()

root.attributes('-fullscreen', True)
w, h = root.winfo_screenwidth(), root.winfo_screenheight()
root.geometry("%dx%d+0+0" % (w, h))
root.title("LRP Photo Booth")
root.option_add("tearOff", False)
read_the_shelve()
menubar=Menu(root)
root['menu'] = menubar
menu_file=Menu(menubar)
menu_edit=Menu(menubar)
menu_setup=Menu(menubar)

menubar.add_cascade(menu=menu_file, label="File")
menu_file.add_command(label="About", command=aboutPage)
menu_file.add_command(label="Exit", command=exitProgram)

menubar.add_cascade(menu=menu_edit, label="Operation")
menu_edit.add_command(label="Set Up the Event", command=SetUpEvent)
menu_edit.add_separator()
menu_edit.add_checkbutton(label="Make a Bride and Groom Message", variable=bandg_check)
menu_edit.add_checkbutton(label="Print Montage", variable=print_check)
menu_edit.add_checkbutton(label="Email Montage", variable=email_check)
menu_edit.add_checkbutton(label="Blog  Montage", variable=blog_check)

menubar.add_cascade(menu=menu_setup, label="Set-up")
menu_setup.add_command(label="Camera Check", command=adminbox)
menu_setup.add_separator()
menu_setup.add_command(label="Clean Images", command=clean_house)
menu_setup.add_separator()
menu_setup.add_checkbutton(label="Play Sound", variable=sound_check)
menu_setup.add_checkbutton(label="Give Feedback", variable=admin_check)
menu_setup.add_separator()
menu_setup.add_command(label="Set up Printer", command=editPrinter)
menu_setup.add_command(label="Set up e-Mail", command=editEmail)
menu_setup.add_command(label="Update Post Text", command=editPostDialog)
menu_setup.add_separator()

mainframe=ttk.Frame(root, padding="15 15 15 15")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))

ttk.Label(mainframe, textvariable=msg).grid(column=2, row=7)
pictureButton=ttk.Button(mainframe, text = "Click Here To Start!", command = TakePicture)
pictureButton.grid(column=2, row=3)

def fix_swap():
	topleft['image']=thumb1
	topleft.image=thumb1
	bottomleft['image']=thumb2
	bottomleft.image=thumb2
	topright['image']=thumb3
	topright.image=thumb3
	bottomright['image']=thumb4
	bottomright.image=thumb4
	root.update()
	
thumb1=PhotoImage(file="1.gif")
topleft=ttk.Label(mainframe, image=thumb1)
topleft.grid(column=1, row=1, rowspan=3, sticky=N)
thumb2=PhotoImage(file="2.gif")
bottomleft=ttk.Label(mainframe, image=thumb2)
bottomleft.grid(column=1, row=4, rowspan=3, sticky=N)
thumb3=PhotoImage(file="3.gif")
topright=ttk.Label(mainframe, image=thumb3)
topright.grid(column=3, row=1, rowspan=3, sticky=N)
thumb4=PhotoImage(file="4.gif")
bottomright=ttk.Label(mainframe, image=thumb4)
bottomright.grid(column=3, row=4, rowspan=3, sticky=N)
thumb5=PhotoImage(file="trans_logo.gif")
top=ttk.Label(mainframe, image=thumb5).grid(column=2, row=1, sticky=(N))
thumb6=PhotoImage(file="tiles.gif")
bottom=ttk.Label(mainframe, image=thumb6).grid(column=2, row=5, sticky=(S))

root_progressbar=ttk.Progressbar(mainframe, orient='horizontal', mode='determinate')
root_progressbar.grid(column=2, row=6, sticky=(W, S, E))
root_progressbar['maximum']=100

for child in mainframe.winfo_children():child.grid_configure(padx=15, pady=15)

mainloop()
