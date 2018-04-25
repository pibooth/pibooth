
.. image:: https://raw.githubusercontent.com/werdeil/pibooth/master/templates/pibooth.png
   :align: center
   :alt: Pibooth


The ``pibooth`` project attempts to provide a Photo Booth application *out-of-the-box*
for Raspberry Pi.

Requirements
------------

The requirements listed below are the one used for the development of ``pibooth``, but other
configuration may work fine. **All hardware buttons, lights and printer are optional**,
the application can be entirely controlled using a standard keyboard.

Hardware
^^^^^^^^

* 1 Raspberry Pi 2 Model B (or higher)
* 1 Camera (Pi Camera v2.1 8 MP 1080p or any camera `compatible with gphoto2
  <http://www.gphoto.org/proj/libgphoto2/support.php>`_)
* 2 push buttons
* 4 LEDs
* 4 resistors of 100 Ohm
* 1 printer

Software
^^^^^^^^

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

   .. hint:: Don't forget to enable the camera in raspi-config.

3. Reboot and open a terminal. Install the latest firmware version:

   ::

        $ sudo rpi-update

4. Upgrade all installed software:

   ::

        $ sudo apt-get update
        $ sudo apt-get upgrade

5. Optionally install ``gphoto2`` (required only for external camera):

   ::

        $ sudo wget raw.github.com/gonzalo/gphoto2-updater/master/gphoto2-updater.sh
        $ sudo chmod 755 gphoto2-updater.sh
        $ sudo ./gphoto2-updater.sh

6. Optionally install ``CUPS`` to handle printers (more instruction to add a new printer can be found
   `here <https://www.howtogeek.com/169679/how-to-add-a-printer-to-your-raspberry-pi-or-other-linux-computer>`_):

   ::

        $ sudo apt-get install cups libcups2-dev

7. Install ``pibooth`` from the `pypi repository <https://pypi.org/project/pibooth/>`_:

   ::

        $ sudo pip3 install pibooth

   .. hint:: If you don't have *gphoto2* and/or *CUPS* installed (steps 5. and/or 6. skipped), use
             the ``--no-deps`` option to avoid installation failures (you may need to install Python
             dependencies by yourself)

Run
---

Start the Photo Booth application using the command::

    $ pibooth

All pictures taken are stored in a subfolder of the one defined in the configuration,
named **YYYY-mm-dd hh-mm-ss** which the time when first picture of the sequence was taken.

Note that if you have both ``Pi`` and ``GPhoto2`` cameras connected to the Raspberry Pi, both are
used. The preview is taken using the ``Pi`` one for a better video rendering and the capture is
taken using the ``GPhoto2`` one for better picture rendering.

You can display a basic help on application options by using the command::

    $ pibooth --help

Commands
^^^^^^^^

After the graphical interface is started, the following actions are available:

==================== ================ =====================
Action               Keyboard key     Physical button
==================== ================ =====================
Toggle Full screen   Ctrl + F         \-
Choose layout        LEFT or RIGHT    Button 1 or Button 2
Take pictures        P                Button 1
Export Printer/Cloud Ctrl + E         Button 2
Quit                 ESC              \-
==================== ================ =====================

States and lights management
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The application follows the states sequence defined in the diagram below:

.. image:: https://raw.githubusercontent.com/werdeil/pibooth/master/templates/state_sequence.png
   :align: center
   :alt: State sequence

The states of the **LED 1** and **LED 2** are modified depending on the actions available
for the user. The **LED 3** is switched on when the application starts and the **LED 4**
is switched on during the preview and photo capture.

Final picture rendering
^^^^^^^^^^^^^^^^^^^^^^^

The ``pibooth`` application  handle the rendering of the final picture using 2 variables defined in
the configuration (see `Configuration`_ below):

* ``[CAMERA][resolution] = (width, height)`` is the resolution of the captured photo in pixels.
  As explained in the configuration file, the preview size is directly dependent from this parameter.
* ``[PICTURE][orientation] = auto/landscape/portrait`` is the orientation of the final picture
  (after concatenation of all captures). If the value is **auto**, the orientation is automatically
  chosen depending on the resolution.

.. note:: The resolution is an important parameter, it is responsible for the quality of the final
          picture. Have a look to `picamera possible resolutions <http://picamera.readthedocs.io/en/latest/fov.html#sensor-modes>`_ .

Run a developing version
------------------------

If you want to use an unofficial version of the ``pibooth`` application, you need to work from a
clone of this ``git`` repository. Replace the step 7. of the `Install`_ procedure above by the
following actions:

- clone from github ::

   $ git clone https://github.com/werdeil/pibooth.git

- go in the cloned directory ::

   $ cd pibooth

- run ``pibooth`` with the command ::

   $ PYTHONPATH=. python3 pibooth/ptb.py

Configuration
-------------

At the first run, a configuration file is generated in ``~/.config/pibooth/pibooth.cfg``
which permits to configure the behavior of the application. The configuration can be
easily edited using the command::

    $ pibooth --config

The default configuration can be restored with the command (strongly recommended when
upgrading ``pibooth``)::

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

    # Start pibooth at Raspberry Pi startup
    autostart = False

    # Show fail message and go back to wait state in case of exception
    failsafe = True

    [WINDOW]
    # (width, height) of the display monitor or 'fullscreen'
    size = (800, 480)

    # Blinking background when picture is taken
    flash = True

    # How long is the preview in seconds
    preview_delay = 3

    # Show a countdown timer during the preview
    preview_countdown = True

    # Stop the preview before taking the picture
    preview_stop_on_capture = False

    [PICTURE]
    # Possible choice(s) of captures numbers (numbers between 1 to 4 max)
    captures = (4, 1)

    # Orientation of the final image ('auto', 'portrait' or 'landscape')
    orientation =  auto

    # First text displayed
    footer_text1 = Footer 1

    # Second text displayed
    footer_text2 = Footer 2

    # Footer text RGB color
    text_color = (0, 0, 0)

    # Background RGB color or path to a background image
    bg_color = (255, 255, 255)

    [CAMERA]
    # Adjust for lighting issues (normal is 100 or 200. Dark is 800 max)
    iso = 100

    # Flip horizontally the captured picture
    flip = False

    # Rotation of the camera (valid values are 0, 90, 180, and 270)
    rotation = 0

    # Resolution for camera captures (preview will have same aspect ratio)
    resolution = (1934, 2464)

    [PRINTER]
    # Name of the printer defined in CUPS (or use the 'default' one)
    printer_name = default

    # How long is the print view in seconds (0 to skip it)
    printer_delay = 10

Printer configuration
---------------------

Here is the default configuration used in CUPS, this may depend on the printer used:

================ =============================
Options          Value
================ =============================
Media Size       10cm x 15cm
Color Model      CMYK
Media Type       Glossy Photo Paper
Resolution       Automatic
2-Sided Printing Off
Shrink page ...  Shrink (print the whole page)
================ =============================

.. note:: The print button (see `Commands`_) and print states are automatically deactivated if:

            * `pycups <https://pypi.python.org/pypi/pycups>`_ is not installed
            * no printer configured in ``CUPS``

Circuit diagram
---------------

.. image:: https://raw.githubusercontent.com/werdeil/pibooth/master/templates/sketch.png
   :align: center
   :alt: Electronic sketch

Credits
-------

Icons from the Noun Project

- Thumb up by Symbolon
- Polaroid by icon 54
- Cat by Внталий Плут
- Up hand drawn arrow by Kid A
- Cameraman and Friends Posing For Camera by Gan Khoon Lay
