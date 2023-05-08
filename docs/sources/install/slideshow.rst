Slideshow
---------

The procedure below describe step by step how to setup a **second** Raspberry Pi
with a slideshow based on `Pi Presents <https://pipresents.wordpress.com/features>`_ ,
to display ``pibooth`` pictures on remote screen. Steps to proceed are summarized here:

.. contents::
   :local:

Install ``Pi Presents``
^^^^^^^^^^^^^^^^^^^^^^^

1. Download the Pi OS **Buster** (with desktop) image and set-up an SD-card. You can follow
   `these instructions <https://www.raspberrypi.org/documentation/installation/installing-images/README.md>`_.

2. Insert the SD-card into the Raspberry Pi and fire it up. Use the
   ``raspi-config`` tool to enable SSH.

3. Upgrade all installed software:

   .. code-block:: bash

        sudo apt-get update
        sudo apt-get full-upgrade

4. Install required software:
   
   .. code-block:: bash

         sudo apt install python3-pil.imagetk unclutter mplayer python3-pexpect python-vlc selenium chromium-driver

5. Install ``Pi Presents``:

   .. code-block:: bash

         mkdir ~/pipresents;cd ~/pipresents
         wget https://github.com/KenT2/pipresents-beep/tarball/master -O - | tar xz --strip-components 1

6. Test ``Pi Presents`` installation. It will display a window with an error message which is because
   there is no profiles defined. Click OK to exit Pi Presents:

   .. code-block:: bash

         python3 ~/pipresents/pipresents.py

Setup ``Pi Presents``
^^^^^^^^^^^^^^^^^^^^^

1. Download ``Pi Presents`` examples and profiles:

   .. code-block:: bash

         mkdir ~/pipresents-profiles;cd ~/pipresents-profiles
         wget https://github.com/KenT2/pipresents-beep-examples/tarball/master /home/pi -O - | tar xz --strip-components 1

2. Run ``pibooth`` liveshow. You should see a presentation (quit by pressing **Alt+F4**):

   .. code-block:: bash

         python3 ~/pipresents/pipresents.py -p pp_mediashow_1p4 -f -b

3. Customize the show:

   .. code-block:: bash

         nano ~/pipresents-profiles/pp_home/pp_profiles/pp_liveshow_1p4/pp_showlist.json

   And modify the following lines:

      -  Delete default background image::
  
         "background-image": "",
      -  Set image size to full screen(fit = resize) x=0 y=0 window with=1920 widow height=1080::
  
         "image-window": "fit 0 0 1920 1080",
      
      -  Pictures should be ordered reverse = last picture first (the author added specially this option for our usage <3)::
         
         "sequence": "reverse",

      - Delete the default text::
  
         "show-text": "",

4. Start ``Pi Presents`` at Raspberry Pi startup:

   .. code-block:: bash

      sudo raspi-config

   and configure::

      system option menu
      Boot / Auto login menu
      Desktop Autologin menu

5. Create autostart file:

   .. code-block:: bash

      mkdir -p ~/.config/lxsession/LXDE-pi
      cp /etc/xdg/lxsession/LXDE-pi/autostart ~/.config/lxsession/LXDE-pi/autostart

6. Edit autostart file:

   .. code-block:: bash

      nano ~/.config/lxsession/LXDE-pi/autostart

   and add this line at the end of the file::

      /usr/bin/python3 ~/pipresents/pipresents.py -o ~/pipresents-profiles -p pp_liveshow_1p4


7. Autorise pi user to execute ``Pi Presents`` at startup:

   .. code-block:: bash

      sudo apt-get install xserver-xorg-legacy
      sudo nano /etc/X11/Xwrapper.config

   and edit the line::

      allowed_users = anybody

Establish SSH connection between both Raspberry Pi
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. Get current IP address

   .. code-block:: bash

      ip route | grep eth0  # If you are using an Ethernet cable

      ip route | grep wlan0  # If you are using a Wifi connection

2. Set a static IP address

   .. code-block:: bash

      sudo nano /etc/dhcpcd.conf

   and add lines (IP from step 1.)::

      interface wlan0
      static ip_address=xxx.xxx.xxx.xxx/24
      static routers=xxx.xxx.xxx.xxx.

3. Restart ``Pi Presents`` Raspberry Pi
   
4. On ``pibooth`` Raspberry Pi, generate an SSH key (press [ENTER] for each question):

   .. code-block:: bash

      ssh-keygen -t rsa

5. Copy your identification key to the ``Pi Presents`` Raspberry Pi (modify xxx.xxx.xxx.xxx to IP from step 1.).
   You will have to confirm (yes) and login with the password of the ``pibooth`` "pi" user:

   .. code-block:: bash

      ssh-copy-id -i ~/.ssh/id_rsa.pub pi@xxx.xxx.xxx.xxx

6. Check that you can login from ``pibooth`` Raspberry Pi to ``Pi Presents`` Raspberry Pi without
   password:

   .. code-block:: bash

      ssh pi@xxx.xxx.xxx.xxx

Create a ``rsync`` script
^^^^^^^^^^^^^^^^^^^^^^^^^

.. note:: The script will synchronize the ``pibooth`` folder from ``pibooth`` Raspberry Pi
          to the ``~/pipresents-profile/pp_home/pp_live_tracks`` (only .jpg files, but not
          file with 0bytes because it crashes the pibooth display)

1. On ``pibooth`` Raspberry Pi, create the file:

   .. code-block:: bash

      nano ~/copy2pipresents.sh

   and add the lines (modify xxx.xxx.xxx.xxx to IP of ``Pi Presents`` Raspberry Pi)::

      #!/bin/bash
      rsync -e ssh -o -avz --min-size=1 /home/pi/Pictures/pibooth/*.jpg pi@xxx.xxx.xxx.xxx:/home/pi/pipresents-profiles/pp_home/pp_live_tracks &

2. Change script permissions:

   .. code-block:: bash

      chmod 777 ~/copy2pipresents.sh

Setup a ``pibooth`` plugin to run ``rsync``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. On ``pibooth`` Raspberry Pi, create the file:

   .. code-block:: bash

      nano ~/pibooth_copy2pipresents.py

   and copy the following code:

   .. code-block:: python

      """Plugin to rsync pictures to pipresents"""
      import os
      import pibooth
      from pibooth.utils import LOGGER

      __version__ ="0.0.1"

      @pibooth.hookimpl
      def state_processing_exit(app):
         LOGGER.info('Uploading picture to remote Pi Presents Raspberry Pi')
         os.popen('~/copy2pipresents.sh')

2. Declare the plugin in ``pibooth`` configuration:

   .. code-block:: bash

      pibooth --config

   and change the following line:

   .. code-block:: ini

      # Path to custom plugin(s) not installed with pip (list of quoted paths accepted)
      plugins = ~/pibooth_copy2pipresents.py

3. Optionnaly, on ``Pi Presents`` Raspberry Pi, erase the pictures at each startup by 
   creatin a cron script:

   .. code-block:: bash

      crontab -e

   and add the line::

      @reboot rm /home/pi/pp_home/pp_live_tracks/*.jpg
