
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

Hardware:
^^^^^^^^^

* 1 Raspberry Pi 2 Model B (or higher)
* 1 Camera (Pi Camera v2.1 8 MP 1080p or any camera `compatible with gphoto2
  <http://www.gphoto.org/proj/libgphoto2/support.php>`_)
* 2 push buttons
* 2 LEDs
* 2 resistors of 100 Ohm
* 1 printer

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

7. Install ``pibooth`` from the pypi repository:

   ::

        $ sudo pip install pibooth

   .. hint:: If you don't have *gphoto2* and/or *CUPS* installed (steps 5. and/or 6. skipped), use
             the ``--no-deps`` option to avoid installation failures (you may need to install Python
             dependencies yourself)

Run
---

Start the Photo Booth application using the command::

    $ pibooth

All pictures taken are stored in a subfolder of the one defined in the configuration,
named **YYYY-mm-dd hh-mm-ss** which the time when first photo of the sequence was taken.

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

Here below is the state sequence of the application and the related lights states.

.. image:: https://raw.githubusercontent.com/werdeil/pibooth/master/templates/state_sequence.png
   :align: center
   :alt: State sequence

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

    [WINDOW]
    # (width, height) of the display monitor or 'fullscreen'
    size = (800, 480)

    # Blinking background when picture is taken
    flash = True

    # How long is the preview in seconds
    preview_delay = 3

    # Show a countdown timer during the preview
    preview_countdown = True

    [PICTURE]
    # Number pictures in case of multiple captures (4 max)
    captures = 4

    # Orientation of the final image (portrait or landscape
    orientation =  portrait

    # First text displayed
    footer_text1 = Footer 1

    # Second text displayed
    footer_text2 = Footer 2

    # Footer text RGB color
    text_color = (0, 0, 0)

    # Background RGB color
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
    # Name of the printer to send the pictures
    printer_name = default

    # How long is the print view in seconds (0 to skip it)
    printer_delay = 10

Run pibooth at startup
----------------------

To run ``pibooth`` in fullscreen at the boot of the raspberry pi follow these instructions:

1. Create a ``pibooth.desktop`` file in the ``~/.config/autostart/`` folder

2. Fill the following info in the file:

.. code-block:: ini

   [Desktop Entry]
   Name=pibooth
   Exec=pibooth
   Type=application

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
- Up hand drawn arrow by Kid A
- Friends by Moriah Rich
- Cameraman by Gan Khoon Lay
