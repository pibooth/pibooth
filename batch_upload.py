#!/usr/bin/env python
# created by chris@drumminhands.com
# Batch upload photos post event, if there was no internet connection at the event
# Note, there are limits to how often/much you can upload to Tumblr via their API. 
# If you have issues, try to upload in smaller batches or less frequently.

import argparse
import os
import glob
import stat
import sys
import time
import pytumblr # https://github.com/tumblr/pytumblr
import config # this is the config file config.py

# global variables
delay = 1 # delay between uploads. Don't abuse the Tumblr server. 

# Setup the tumblr OAuth Client
client = pytumblr.TumblrRestClient(
    config.consumer_key,
    config.consumer_secret,
    config.oath_token,
    config.oath_secret,
)

def main():
	if config.make_gifs:
		files = glob.glob(config.file_path + '*.gif')
		files.sort() # organize the list
		for f in files:
			uploadOne(f)
	else:
		files = glob.glob(config.file_path + '*.jpg')
		files.sort() # organize the list
		
		previous_group = "0000-00-00-00-00-00" # used to not duplicate groups
		
		for f in files:
			current_group = f[len(config.file_path):]
			current_group = current_group[:19]
			if (current_group != previous_group): # remove duplicates
				uploadMultiple(current_group) #upload a group of pics
				print "Uploaded: " + current_group
				previous_group = current_group # remember for next time through loop

	print "Completed uploading pics"
	
def uploadOne(pic):	
	while True: 
		try:
			file_to_upload = pic
			print "Uploading " + file_to_upload
			client.create_photo(config.tumblr_blog, state="published", tags=[config.tagsForTumblr], data=file_to_upload)
			time.sleep(delay) # wait a bit
# 			cmd = "mv " + file_to_upload + " " + config.file_path + "/batch_uploaded"
# 			os.system(cmd) # once uploaded, move to sub directory
			break
		except ValueError:
			print pic + " not uploaded. Error."					

def uploadMultiple(group_name):
	while True: 
		try:
			# create an array and populate with file paths to our jpgs
			myJpgs=[0 for i in range(4)]
			for i in range(4):
				myJpgs[i]=config.file_path + group_name + "-0" + str(i+1) + ".jpg"
			
			# upload files into one post
			client.create_photo(config.tumblr_blog, state="published", tags=[config.tagsForTumblr], format="markdown", data=myJpgs)
			
			# wait a bit
			time.sleep(delay)
				
			break
		except ValueError:
			print group_name + " not uploaded. Error."
				
print 'Batch Upload Start'

# run the main program
main()
