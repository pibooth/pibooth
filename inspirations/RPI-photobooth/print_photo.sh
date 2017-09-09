#!/bin/bash
mogrify -resize 968x648 /home/pi/photobooth/*.jpg
montage /home/pi/photobooth/*.jpg -tile 2x2 -geometry +10+10 /home/pi/photobooth/montage.jpg
lp -d Canon_CP910 /home/pi/photobooth/montage.jpg
sudo rm /home/pi/photobooth/*.jpg