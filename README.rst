|Pibooth| |BeerPay|

|PythonVersions| |PypiPackage| |Downloads|

The ``pibooth`` project provides a photobooth application *out-of-the-box* in pure Python
for Raspberry Pi. Have a look to the `wiki <https://github.com/pibooth/pibooth/wiki>`_
to discover some realizations from GitHub users, and don't hesitate to send us photos of your version.

.. image:: https://raw.githubusercontent.com/pibooth/pibooth/master/templates/background_samples.png
   :align: center
   :alt: Settings

.. note:: Even if designed for a Raspberry Pi, this software may be installed on any Unix/Linux
          based OS (tested on Ubuntu 16 and Mac OSX 10.14.6).

.. contents::

Features
--------

* Interface available in Danish, Dutch, English, French, German, Hungarian, Norwegian and Spanish (customizable)
* Capture from 1 to 4 photos and concatenate them in a final picture
* Support all cameras compatible with gPhoto2, OpenCV and Raspberry Pi
* Support for hardware buttons and lamps on Raspberry Pi GPIO
* Fully driven from hardware buttons / keyboard / mouse / touchscreen
* Auto-start at the Raspberry Pi startup
* Animate captures from the last sequence during idle time
* Store final pictures and the individual captures
* Printing final pictures using CUPS server (printing queue indication)
* Custom texts can be added on the final picture (customizable fonts, colors, alignments)
* Custom background(s) and overlay(s) can be added on the final picture
* All settings available in a configuration file (most common options in a graphical interface)
* Highly customizable thanks to its plugin system, you can develop your own plugin

Gallery
-------

You can see some examples of the output picture formats you can get with ``pibooth`` on the following page.

.. image:: https://raw.githubusercontent.com/pibooth/pibooth/master/templates/gallery.png
   :align: center
   :alt: gallery
   :target: https://github.com/pibooth/pibooth/blob/master/docs/examples.rst
   :height: 200px

Requirements
------------

The requirements listed below are the ones used for the development of ``pibooth``, but
other configuration may work fine. **All hardware buttons, lights and printer are optional**,
the application can be entirely controlled using a keyboard, a mouse or a touchscreen.

.. warning:: Using a Pi Camera, the preview is visible only on a screen connected to the HDMI or
             DSI connectors (the preview is an overlay managed at GPU low level).

Hardware
^^^^^^^^

* 1 Raspberry Pi 3 Model B (or higher)
* 1 Camera (Raspberry Pi Camera v2.1 8 MP 1080p
  or any DSLR camera `compatible with gPhoto2 <http://www.gphoto.org/proj/libgphoto2/support.php>`_
  or any webcam `compatible with OpenCV <https://opencv.org>`_ )
* 2 push buttons
* 2 LEDs
* 2 resistors of 100 Ohm
* 1 printer

Software
^^^^^^^^

* Raspbian ``Raspberry Pi OS with desktop``
* Python ``3.7.3``
* libsdl2 ``2.0``
* libgphoto2 ``2.5.27``
* libcups ``2.2.10``

Install
-------

A brief description on how to set-up a Raspberry Pi to use this software.

1. Download the Raspbian image and set-up an SD-card. You can follow
   `these instructions <https://www.raspberrypi.org/documentation/installation/installing-images/README.md>`_.

2. Insert the SD-card into the Raspberry Pi and fire it up. Use the ``raspi-config`` tool
   to configure your system (e.g., expand partition, change hostname, password, enable SSH,
   configure to boot into GUI, etc.).

   .. hint:: Don't forget to enable the camera in raspi-config.

3. Upgrade all installed software:

   ::

        $ sudo apt-get update
        $ sudo apt-get full-upgrade

4. Install SDL2 (and extras) which is required by ``pygame 2+``:

   ::

        $ sudo apt-get libsdl2-*

5. Optionally install the last stable ``gPhoto2`` version (required only for DSLR camera):

   ::

        $ sudo wget raw.github.com/gonzalo/gphoto2-updater/master/gphoto2-updater.sh
        $ sudo chmod 755 gphoto2-updater.sh
        $ sudo ./gphoto2-updater.sh

6. Optionally install ``CUPS`` to handle printers (more instructions to add a new printer can be found
   `here <https://www.howtogeek.com/169679/how-to-add-a-printer-to-your-raspberry-pi-or-other-linux-computer>`_):

   ::

        $ sudo apt-get install cups libcups2-dev

7. Optionally install ``OpenCV`` to improve images generation efficiency or if a Webcam is used:

   ::

        $ sudo apt-get install python3-opencv

8. Install ``pibooth`` from the `pypi repository <https://pypi.org/project/pibooth/>`_:

   ::

        $ sudo pip3 install pibooth[dslr,printer]

   .. hint:: If you don't have ``gPhoto2`` and/or ``CUPS`` installed (steps 5. and/or 6. skipped), remove
             printer or dslr under the ``[]``

.. note:: An editable/customizable version of ``pibooth`` can be installed by following
          these `instructions <https://github.com/pibooth/pibooth/blob/master/docs/dev.rst>`_ .
          Be aware that the code on the `master` branch may be unstable.

Run
---

Start the photobooth application using the command::

    $ pibooth

All pictures taken are stored in the folder defined in ``[GENERAL][directory]``. They are named
**YYYY-mm-dd-hh-mm-ss_pibooth.jpg** which is the time when first capture of the sequence was taken.
A subfolder **raw/YYYY-mm-dd-hh-mm-ss** is created to store the single raw captures.

.. note:: if you have both ``Pi`` and ``DSLR`` cameras connected to the Raspberry Pi, **both are used**,
          this is called the **Hybrid** mode. The preview is taken using the ``Pi`` one for a better
          video rendering and the capture is taken using the ``DSLR`` one for better picture rendering.

You can display a basic help on application options by using the command::

    $ pibooth --help

States and lights management
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The application follows the states sequence defined in the simplified diagram
below:

.. image:: https://raw.githubusercontent.com/pibooth/pibooth/master/templates/state_sequence.png
   :align: center
   :alt: State sequence

The states of the **LED 1** and **LED 2** are modified depending on the actions available
for the user.

Detailed state diagram can be found `on this page <https://github.com/pibooth/pibooth/blob/master/docs/plugin.rst>`_.

Commands
^^^^^^^^

After the graphical interface is started, the following actions are available:

======================= ================ =====================
Action                  Keyboard key     Physical button
======================= ================ =====================
Toggle Full screen      Ctrl + F         \-
Choose layout           LEFT or RIGHT    Button 1 or Button 2
Take pictures           P                Button 1
Export Printer/Cloud    Ctrl + E         Button 2
Open/close settings     ESC              Button 1 + Button 2
Select option           UP or DOWN       Button 1
Change option value     LEFT or RIGHT    Button 2
======================= ================ =====================

Final picture rendering
^^^^^^^^^^^^^^^^^^^^^^^

The ``pibooth`` application handle the rendering of the final picture using 2 variables defined in
the configuration (see `Configuration`_ below):

* ``[CAMERA][resolution] = (width, height)`` is the resolution of the captured picture in pixels.
  As explained in the configuration file, the preview size is directly dependent from this parameter.
* ``[PICTURE][orientation] = auto/landscape/portrait`` is the orientation of the final picture
  (after concatenation of all captures). If the value is **auto**, the orientation is automatically
  chosen depending on the resolution.

.. note:: The resolution is an important parameter, it is responsible for the quality of the final
          picture. Have a look to `picamera possible resolutions <http://picamera.readthedocs.io/en/latest/fov.html#sensor-modes>`_ .

Image effects can be applied on the capture using the ``[PICTURE][effect]`` variable defined in the
configuration.

.. code-block:: ini

    [PICTURE]

    # Effect applied on all captures
    captures_effects = film

Instead of one effect name, a list of names can be provided. In this case, the effects are applied
sequentially on the captures sequence.

.. code-block:: ini

    [PICTURE]

    # Define a rolling sequence of effects. For each capture the corresponding effect is applied.
    captures_effects = ('film', 'cartoon', 'washedout', 'film')

Have a look to the predefined effects available depending on the camera used:

* `picamera effects <https://picamera.readthedocs.io/en/latest/api_camera.html#picamera.PiCamera.image_effect>`_
* `gPhoto2 effects (PIL based) <https://pillow.readthedocs.io/en/latest/reference/ImageFilter.html>`_

Texts can be defined by setting the option ``[PICTURE][footer_text1]`` and ``[PICTURE][footer_text2]``
(lets them empty to hide any text). For each one, the font, the color and the alignment can be chosen.
For instance:

.. code-block:: ini

    [PICTURE]

    # Same font applied on footer_text1 and footer_text2
    text_fonts = Amatic-Bold

This key can also take two names or TTF file paths:

.. code-block:: ini

    [PICTURE]

    # 'arial' font applied on footer_text1, 'Roboto-BoldItalic' font on footer_text2
    text_fonts = ('arial', 'Roboto-BoldItalic')

The available fonts can be listed using the following the command::

    $ pibooth --fonts

To regenerate the final pictures afterwards, from the originals captures present in the
``raw`` folder, use the command::

    $ pibooth-regen

It permits to adjust the configuration to enhance the previous pictures with better
parameters (title, more effects, etc...)

Configuration
-------------

At the first run, a configuration file is generated in ``~/.config/pibooth/pibooth.cfg``
which permits to configure the behavior of the application.

A quick configuration GUI menu (see `Commands`_ ) gives access to the most common options:

.. image:: https://raw.githubusercontent.com/pibooth/pibooth/master/templates/settings.png
   :align: center
   :alt: Settings

More options are available by editing the configuration file which is easily
done using the command::

    $ pibooth --config

The default configuration can be restored with the command (strongly recommended when
upgrading ``pibooth``)::

    $ pibooth --reset

See the `default configuration file <https://github.com/pibooth/pibooth/blob/master/docs/config.rst>`_
for further details.

Customize using plugins
^^^^^^^^^^^^^^^^^^^^^^^

Several plugins maintained by the community are available. They add extra features to
``pibooth``. Have a look to the `plugins on PyPI  <https://pypi.org/search/?q=pibooth>`_.

You can also easily develop your own plugin, and declare it in the ``[GENERAL][plugins]``
key of the configuration. See guidelines to
`develop custom plugin <https://github.com/pibooth/pibooth/blob/master/docs/plugin.rst>`_.

GUI translations
^^^^^^^^^^^^^^^^

The graphical interface texts are available in 8 languages by default: Danish, Dutch, English,
French, German, Hungarian, Norwegian and Spanish. The default translations can be easily edited using the command::

    $ pibooth --translate

A new language can be added by adding a new section (``[alpha-2-code]``).
If you want to have ``pibooth`` in your language feel free to send us the corresponding keywords via a GitHub issue.

Printer
^^^^^^^

The print button (see `Commands`_) and print states are automatically activated/shown if:

* `pycups <https://pypi.python.org/pypi/pycups>`_ and `pycups-notify <https://github.com/anxuae/pycups-notify>`_ are installed
* at least one printer is configured in `CUPS <http://localhost:631/printers>`_
* the key ``[PRINTER][printer_name]`` is equal to ``default`` or an existing printer name

To avoid paper waste, set the option ``[PRINTER][max_duplicates]`` to the maximum
of identical pictures that can be sent to the printer.

Set the option ``[PRINTER][max_pages]`` to the number of paper sheets available on the
printer. When this number is reached, the print function will be disabled and an icon
indicates the printer failure. To reset the counter, open then close the settings
graphical interface (see `Commands`_).

Here is the default configuration used for this project in CUPS, it may depend on
the printer used:

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

Here is the diagram for hardware connections. Please refer to the
`default configuration file <https://github.com/pibooth/pibooth/blob/master/docs/config.rst>`_
to know the default pins used (`physical pin numbering <https://pinout.xyz>`_).

.. image:: https://raw.githubusercontent.com/pibooth/pibooth/master/templates/sketch.png
   :align: center
   :alt: Electronic sketch

An extra button can be added to start and shutdown properly the Raspberry Pi.
Edit the file ``/boot/config.txt`` and set the line::

    dtoverlay=gpio-shutdown

Then connect a push button between physical *pin 5* and *pin 6*.

Terms and conditions
--------------------

See the LICENSE file to have details on the terms and coniditions.

GDPR advices
^^^^^^^^^^^^

``pibooth`` was developed for a private usage with no connection to a professional or commercial activity,
as a consequence GDPR does not apply.
However if you are using photobooth in Europe, it is your responsability to check that your usage and
more particularly the usage of the pictures generated by ``pibooth`` follows the GDPR rules, especially make
sure that the people that will use the ``pibooth`` are aware that the image will be stored on the device.

Credits
^^^^^^^

Pibooth icon from `Artcore Illustrations <https://www.iconspedia.com/icon/photobooth-icon-29464.html>`_

Icons from the Noun Project (https://thenounproject.com/)

- Polaroid by icon 54
- Up hand drawn arrow by Kid A
- Cameraman and Friends Posing For Camera by Gan Khoon Lay
- Camera by Alfa Design
- Print Photo by Kmg Design
- Pointer hand by Peter van Driel

Support us on Beerpay
---------------------

If you want to help us you can by clicking on the following links!

|BeerPay| |BeerPay2|

.. |BeerPay| image:: https://beerpay.io/werdeil/pibooth/badge.svg?style=beer-square
   :align: middle
   :target: https://beerpay.io/werdeil/pibooth

.. |BeerPay2| image:: https://beerpay.io/werdeil/pibooth/make-wish.svg?style=flat-square
   :align: middle
   :target: https://beerpay.io/werdeil/pibooth?focus=wish

.. |Pibooth| image:: https://raw.githubusercontent.com/pibooth/pibooth/master/templates/pibooth.png
   :align: middle

.. |PythonVersions| image:: https://img.shields.io/badge/python-2.7+ / 3.6+-red.svg
   :target: https://www.python.org/downloads
   :alt: Python 2.7+/3.6+

.. |PypiPackage| image:: https://badge.fury.io/py/pibooth.svg
   :target: https://pypi.org/project/pibooth
   :alt: PyPi package

.. |Downloads| image:: https://img.shields.io/pypi/dm/pibooth?color=purple
   :target: https://pypi.org/project/pibooth
   :alt: PyPi downloads
