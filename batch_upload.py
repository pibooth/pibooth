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
	files = glob.glob(config.file_path + '*')
	for f in files:
		#upload code
		uploadOne(f)
	print "Completed uploading pics"
	
def uploadOne(pic):	
	while True: 
		try:
			file_to_upload = pic
			print "Uploading " + file_to_upload
			client.create_photo(config.tumblr_blog, state="published", tags=[config.tagsForTumblr], data=file_to_upload)
			time.sleep(delay) # wait a bit
			break
		except ValueError:
			print pic + " not uploaded. Error."					
				
print 'Batch Upload Start'

# run the main program
main()
