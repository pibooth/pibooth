
.. image:: https://raw.githubusercontent.com/werdeil/pibooth/master/templates/pibooth.png
   :align: center
   :alt: Pibooth


The ``pibooth`` project attempts to provide a Photo Booth application *out-of-the-box*
for Raspberry Pi.

Requirements
------------

The requirements listed below are the one used for the development of ``pibooth``, but
other configuration may work fine. All hardware buttons and lights are optional.

Hardware:
^^^^^^^^^

* 1 Raspberry Pi Model B+
* 1 Camera (Pi Camera v2.1 8 MP 1080p or any camera `compatible with gphoto2
  <http://www.gphoto.org/proj/libgphoto2/support.php>`_)
* 2 push buttons
* 2 LED
* 2 resistor of 100 Ohm

Software:
^^^^^^^^^

* Python ``3.5.3``
* RPi.GPIO ``0.6.3``
* picamera ``1.13``
* Pillow ``4.0.0``
* pygame ``1.9.3``
* gphoto2 ``1.8.0`` ( libgphoto2 ``2.5.15`` )
* pycups ``1.9.73`` ( CUPS ``2.2.1`` )

Install
-------

A brief description on how to set-up a Raspberry Pi to use this software.

1. Download latest Raspbian image and set-up an SD-card. You can follow
   `these instructions <https://www.raspberrypi.org/documentation/installation/installing-images/README.md>`_ .

2. Insert the SD-card into the Raspberry Pi and fire it up. Use the raspi-config tool that is shown
   automatically on the first boot to configure your system (e.g., expand partition, change hostname,
   password, enable SSH, configure to boot into GUI, etc.).

   .. hint:: Don't forget to enable the camera in raspi-config. A reboot is needed after this.

3. Reboot and open a terminal. Install the latest firmware version:

   ::

        $ sudo rpi-update

4. Upgrade all installed software:

   ::

        $ sudo apt-get update
        $ sudo apt-get upgrade

5. Install ``gphoto2`` (required only for external camera):

   ::

        $ sudo wget raw.github.com/gonzalo/gphoto2-updater/master/gphoto2-updater.sh
        $ sudo chmod 755 gphoto2-updater.sh
        $ sudo ./gphoto2-updater.sh

6. Install ``CUPS`` to handle printers (more instruction to add a new printer can be found
   `here <https://www.howtogeek.com/169679/how-to-add-a-printer-to-your-raspberry-pi-or-other-linux-computer>`_):

   ::

        $ sudo apt-get install cups libcups2-dev

7. Install ``pibooth`` from the pypi repository:

   ::

        $ sudo pip install pibooth

Run
---

Start the Photo Booth application using the command::

    $ pibooth

After the graphical interface is started, the following actions are available:

==================== ================ ================
Action               Keyboard key     Physical button
==================== ================ ================
Toggle Full screen   Ctrl + F         \-
Take pictures        P                Button 1
Export Printer/Cloud Ctrl + E         Button 2
Quit                 ESC              \-
==================== ================ ================

All pictures taken are stored in a subfolder of the one defined in the configuration,
named **YYYY-mm-dd hh-mm-ss** which the time when first photo of the sequence was taken.

Configuration
-------------

At the first run, a configuration file is generated in ``~/.config/pibooth/pibooth.cfg``
which permits to configure the behavior of the application. The configuration can be
easily edited using the command::

    $ pibooth --config

The default configuration can be restored with the command::

    $ pibooth --reset

Below is the default configuration file:

.. code-block:: ini

    [GENERAL]
    # User interface language (fallback to English if not found)
    language = en

    # Path to save pictures
    directory = ~/Pictures/pibooth

    # Cleanup the 'directory' before start
    clear_on_startup = True

    # How long to debounce the button in seconds
    debounce_delay = 0.3

    # Name of the printer to send the pictures
    printer_name = default

    [WINDOW]
    # (Width, Height) of the display monitor
    size = (800, 480)

    # Blinking background when picture is taken
    flash = True

    # How long is the preview in seconds
    preview_delay = 3

    # Show a countdown timer during the preview
    preview_countdown = True

    [PICTURE]
    # How many pictures to take (4 max)
    captures = 4

    # First text displayed
    footer_text1 = Footer 1

    # Second text displayed
    footer_text2 = Footer 2

    # Footer text RGB color
    text_color = (0, 0, 0)

    # Background RGB color
    bg_color = (255, 255, 255)

    [CAMERA]
    # Resolution for camera captures (see picamera modes)
    resolution = (1920, 1080)

    # Adjust for lighting issues. Normal is 100 or 200. Dark is 800 max
    iso = 100

    # Rotation of the camera (valid values are 0, 90, 180, and 270)
    rotation = 0

Circuit diagram
---------------

.. image:: https://raw.githubusercontent.com/werdeil/pibooth/master/templates/sketch.png
   :align: center
   :alt: Electronic sketch

Credits:
--------

Icons from the Noun Project

- Thumb up by Symbolon
- Polaroid by icon 54
- Cat by Внталий Плут
