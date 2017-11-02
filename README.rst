
.. image:: templates/pibooth.png
   :align: center
   :alt: Pibooth


The ``pibooth`` project attempts to provide a Photo Booth application *out-of-the-box*
for Raspberry Pi.

Requirements
------------

* RPi.GPIO
* picamera
* Pillow
* pygame

Install
-------

The project will be available soon on Pypi.

::

    $ pip install pibooth

Run
---

::

    $ pibooth

After the graphical interface is started, the following commands are available:

==================== ================ ================
Action               Keyboard key     Physical button
==================== ================ ================
Toggle Full screen   Ctrl + F         \-
Take pictures        P                Button 1
Export Printer/Cloud Ctrl + E         Button 2
Quit                 ESC              \-
==================== ================ ================

Configuration
-------------

At the first run, a configuration file is generated in ``~/.config/pibooth/pibooth.cfg``
which permits to configure the behavior of the application.

.. code-block:: ini

    [GENERAL]
    # Path to save images
    directory = ~/Pictures/pibooth

    # Clear previously stored photos
    clear_on_startup = True

    # How long to debounce the button in milliseconds
    debounce_delay = 300

    [WINDOW]
    # (Width, Height) of the display monitor
    size = (800, 480)

    # Show a counter between taking photos
    capture_counter = True

    # How long is the preview (in seconds)
    preview_delay = 3

    # Preview window position related to the main window
    preview_offset = (50, 60)

    [PICTURE]
    # How many pictures to take (max 4)
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
    resolution = (3280, 2464)

    # Adjust for lighting issues. Normal is 100 or 200. Dark is 800 max
    iso = 100

Circuit diagram
---------------

.. image:: templates/sketch.png
   :height: 990 px
   :width: 1215 px
   :scale: 50 %
   :align: center
   :alt: electronic sketch

Credits:
--------

Icons from the Noun Project

 - Button by Prerak Patel
 - Disco pose by Moriah Rich
 - Fireworks by Creative Stall
 - Hamster wheel by Dream Icons
 - Tap by Prerak Patel
 - Yoga poses by Claire Jones

Other inspirations:

 - https://github.com/drumminhands/drumminhands_photobooth
 - http://www.instructables.com/lesson/Build-a-Photo-Booth/
 - http://www.instructables.com/id/Raspberry-Pi-photo-booth-controller/
 - http://www.instructables.com/id/Lininger-Rood-Photo-Booth/
