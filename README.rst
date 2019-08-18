
.. image:: https://raw.githubusercontent.com/werdeil/pibooth/master/templates/pibooth.png
   :align: center
   :alt: Pibooth


The ``pibooth`` project attempts to provide a photobooth application *out-of-the-box*
in pure Python for Raspberry Pi. Have a look to the `wiki <https://github.com/werdeil/pibooth/wiki>`_
to discover some realizations from GitHub users.

.. image:: https://raw.githubusercontent.com/werdeil/pibooth/master/templates/background_samples.png
   :align: center
   :alt: Settings

Requirements
------------

The requirements listed below are the ones used for the development of ``pibooth``, but
other configuration may work fine. **All hardware buttons, lights and printer are optional**,
the application can be entirely controlled using a keyboard, a mouse or a touchsceen.

Hardware
^^^^^^^^

* 1 Raspberry Pi 2 Model B (or higher)
* 1 Camera (Pi Camera v2.1 8 MP 1080p or any DSLR camera `compatible with gPhoto2
  <http://www.gphoto.org/proj/libgphoto2/support.php>`_)
* 2 push buttons
* 4 LEDs
* 4 resistors of 100 Ohm
* 1 printer

Software
^^^^^^^^

* Raspbian ``Buster with desktop and recommended software``
* Python ``3.5.3``
* libgphoto2 ``2.5.23``
* libcups ``2.2.1``

Install
-------

A brief description on how to set-up a Raspberry Pi to use this software.

1. Download the Raspbian image and set-up an SD-card. You can follow
   `these instructions <https://www.raspberrypi.org/documentation/installation/installing-images/README.md>`_ .

2. Insert the SD-card into the Raspberry Pi and fire it up. Use the ``raspi-config`` tool
   to configure your system (e.g., expand partition, change hostname, password, enable SSH,
   configure to boot into GUI, etc.).

   .. hint:: Don't forget to enable the camera in raspi-config.

3. Upgrade all installed software:

   ::

        $ sudo apt-get update
        $ sudo apt-get upgrade

4. Optionally install the last stable ``gPhoto2`` version (required only for DSLR camera):

   ::

        $ sudo wget raw.github.com/gonzalo/gphoto2-updater/master/gphoto2-updater.sh
        $ sudo chmod 755 gphoto2-updater.sh
        $ sudo ./gphoto2-updater.sh

5. Optionally install ``CUPS`` to handle printers (more instructions to add a new printer can be found
   `here <https://www.howtogeek.com/169679/how-to-add-a-printer-to-your-raspberry-pi-or-other-linux-computer>`_):

   ::

        $ sudo apt-get install cups libcups2-dev

6. Optionally install ``OpenCV`` to improve images generation efficiency:

   ::

        $ sudo apt-get install python3-opencv

7. Install ``pibooth`` from the `pypi repository <https://pypi.org/project/pibooth/>`_:

   ::

        $ sudo pip3 install pibooth

   .. hint:: If you don't have ``gPhoto2`` and/or ``CUPS`` installed (steps 5. and/or 6. skipped), use
             the ``--no-deps`` option to avoid installation failures (you may need to install Python
             dependencies by yourself)

.. note:: an editable/customizable version of ``pibooth`` can be installed by following
          `instructions <https://github.com/werdeil/pibooth/blob/master/docs/dev.rst>`_ .
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

The application follows the states sequence defined in the diagram below:

.. image:: https://raw.githubusercontent.com/werdeil/pibooth/master/templates/state_sequence.png
   :align: center
   :alt: State sequence

The states of the **LED 1** and **LED 2** are modified depending on the actions available
for the user. The **LED 3** is switched on when the application starts and the **LED 4**
is switched on during the preview and photo capture.

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

A word about capture effects
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Image effects can be applied on the capture using the ``[PICTURE][effect]`` variable defined in the
configuration.

.. code-block:: ini

    [PICTURE]

    # Effect applied on all captures
    effect = film

Instead of one effect name, a list of names can be provided. In this case, the effects are applied
sequentially on the captures sequence.

.. code-block:: ini

    [PICTURE]

    # Define a rolling sequence of effects. For each capture the corresponding effect is applied.
    effect = ('film', 'cartoon', 'washedout', 'film')

Have a look to the predefined effects available depending on the camera used:

* `picamera effects <https://picamera.readthedocs.io/en/latest/api_camera.html#picamera.PiCamera.image_effect>`_
* `gPhoto2 effects (PIL based) <https://pillow.readthedocs.io/en/latest/reference/ImageFilter.html>`_


Final picture rendering
^^^^^^^^^^^^^^^^^^^^^^^

The ``pibooth`` application  handle the rendering of the final picture using 2 variables defined in
the configuration (see `Configuration`_ below):

* ``[CAMERA][resolution] = (width, height)`` is the resolution of the captured picture in pixels.
  As explained in the configuration file, the preview size is directly dependent from this parameter.
* ``[PICTURE][orientation] = auto/landscape/portrait`` is the orientation of the final picture
  (after concatenation of all captures). If the value is **auto**, the orientation is automatically
  chosen depending on the resolution.

.. note:: The resolution is an important parameter, it is responsible for the quality of the final
          picture. Have a look to `picamera possible resolutions <http://picamera.readthedocs.io/en/latest/fov.html#sensor-modes>`_ .

The fonts used on the final picture can be customized using the configuration key ``[PICTURE][fonts]``.

.. code-block:: ini

    [PICTURE]

    # Same font applied on footer_text1 and footer_text2
    text_fonts = Amatic-Bold

This key can take two name/path/url:

.. code-block:: ini

    [PICTURE]

    # 'arial' font applied on footer_text1, 'Roboto-BoldItalic' font on footer_text2
    text_fonts = ('arial', 'Roboto-BoldItalic')

The available fonts can be listed using the following the command::

    $ pibooth --fonts

Configuration
-------------

At the first run, a configuration file is generated in ``~/.config/pibooth/pibooth.cfg``
which permits to configure the behavior of the application.

A quick configuration GUI menu (see `Commands`_ ) gives access to the most common options:

.. image:: https://raw.githubusercontent.com/werdeil/pibooth/master/templates/settings.png
   :align: center
   :alt: Settings

More options are available by editing the configuration file which is easily
done using the command::

    $ pibooth --config

The default configuration can be restored with the command (strongly recommended when
upgrading ``pibooth``)::

    $ pibooth --reset

See the `default configuration file <https://github.com/werdeil/pibooth/blob/master/docs/config.rst>`_
for further details.

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

Here is the diagram for hardware connections. Please refer to the
`default configuration file <https://github.com/werdeil/pibooth/blob/master/docs/config.rst>`_
to know the default pins used.

.. image:: https://raw.githubusercontent.com/werdeil/pibooth/master/templates/sketch.png
   :align: center
   :alt: Electronic sketch

Credits
-------

Icons from the Noun Project

- Polaroid by icon 54
- Up hand drawn arrow by Kid A
- Cameraman and Friends Posing For Camera by Gan Khoon Lay
