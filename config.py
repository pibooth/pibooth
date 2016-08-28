# Tumblr Setup
# Replace the values with your information
# OAuth keys can be generated from https://api.tumblr.com/console/calls/user/info
consumer_key='CONSUMER_KEY' #replace with your key
consumer_secret='CONSUMER_SECRET' #replace with your secret code
oath_token='OATH_TOKEN' #replace with your oath token
oath_secret='OATH_SECRET' #replace with your oath secret code
tumblr_blog = 'TUMBLR_BLOG' # replace with your tumblr account name without .tumblr.com
tagsForTumblr = "MyTagsHere" # change to tags you want, separated with commas

#Config settings to change behavior of photobooth
file_path = '/home/pi/photobooth/pics/' # path to save images
clear_on_startup = False # True will clear previously stored photos as the program launches. False will leave all previous photos.
debounce = 0.3 # how long to debounce the button. Add more time if the button triggers too many times.
post_online = True  # True to upload images. False to store locally only.
hi_res_pics = False # True to save high res pics from camera.
                    # If also uploading, the program will also convert each image to a smaller image before making the gif.
                    # False to first capture low res pics. False is faster.
monitor_w = 800     # width of the display monitor
monitor_h = 480     # height of the display monitor
