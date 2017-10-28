
.. image:: pibooth/pictures/pibooth.png
<<<<<<< HEAD
   :height: 100px
   :width: 100 px
=======
   :scale: 50 %
>>>>>>> 583ca70a313c9f6dc69fac9b72d3d3e30fbea2a6
   :align: center
   :alt: pibooth

------

pibooth
=======

The ``pibooth`` project attempts to provide a Photo Booth application *out-of-the-box*
for Raspberry Pi.
<<<<<<< HEAD

Requirements
------------

* RPi.GPIO
* picamera
* Pillow

Install
-------

The project will be available soon on Pypi.

::

    $ pip install pibooth

A `wheel` archive can be generated using the setup in the repository.

::

    $ python setup.py bdist_wheel

Run
---

::

    $ pibooth

Configuration
-------------

At the first run, a configuration file is generated in ``~/.config/pibooth/pibooth.cfg``
which permits to configure the behavior of the application.

.. code-block:: ini

    [GENERAL]
    #How long to debounce the button
    debounce_delay = 0.3

=======

Install
-------

The project will be available soon on Pypi.

::

    $ pip install pibooth

A `wheel` archive can be generated using the setup in the repository.

::

    $ python setup.py bdist_wheel

Run
---

    ::

        $ pibooth

Configuration
-------------

At the first run, a configuration file is generated in ``~/.config/pibooth/pibooth.cfg``
which permits to configure the behavior of the application.

::

    [GENERAL]
    #How long to debounce the button
    debounce_delay = 0.3

>>>>>>> 583ca70a313c9f6dc69fac9b72d3d3e30fbea2a6
    #Clear previously stored photos
    clear_on_startup = True

    #Path to save images
    directory = ~/Pictures/pibooth

    [WINDOW]
    #Height of the display monitor
    height = 480

    #Show a counter between taking photos
    capture_counter = True

    #Width of the display monitor
    width = 800

    [MERGED]
    #Background RGB color
    bg_color = (23, 45, 245)

    #Footer text RGB color
    text_color = (0, 0, 0)

    #Second text displayed
    footer_text2 = Footer 2

    #First text displayed
    footer_text1 = Footer 1

    [CAMERA]
    #How long is the preview (in seconds)
    preview_delay = 3

    #High resolution pictures from camera
    high_resolution = True

    #How many pictures to take (max 4)
    captures = 4

    #Adjust for lighting issues. Normal is 100 or 200. Dark is 800 max
    camera_iso = 100

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
