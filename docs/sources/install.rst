Install
-------

A brief description on how to set-up a Raspberry Pi to use this software.

1. Download the Raspbian image and set-up an SD-card. You can follow
   `these instructions <https://www.raspberrypi.org/documentation/installation/installing-images/README.md>`_.

2. Insert the SD-card into the Raspberry Pi and fire it up. Use the
   ``raspi-config`` tool to configure your system (e.g., expand partition,
   change hostname, password, enable SSH, configure to boot into GUI, etc.).

.. hint:: Don't forget to enable the camera in raspi-config.

3. Upgrade all installed software:

.. code-block:: bash

        sudo apt-get update
        sudo apt-get full-upgrade

4. Install SDL2 (and extras) which is required by ``pygame 2+``:

.. code-block:: bash

        sudo apt-get install libsdl2-*

5. Optionally install the last stable ``gPhoto2`` version (required only for
   DSLR camera):

.. code-block:: bash

        sudo wget raw.github.com/gonzalo/gphoto2-updater/master/gphoto2-updater.sh
        sudo chmod 755 gphoto2-updater.sh
        sudo ./gphoto2-updater.sh

6. Optionally install ``CUPS`` to handle printers (more instructions to add a
   new printer can be found `here <https://www.howtogeek.com/169679/how-to-add-a-printer-to-your-raspberry-pi-or-other-linux-computer>`_
   ):

.. code-block:: bash

        sudo apt-get install cups libcups2-dev

7. Optionally install ``OpenCV`` to improve images generation efficiency or if a
   Webcam is used:

.. code-block:: bash

        sudo apt-get install python3-opencv

8. Install ``pibooth`` from the `pypi repository <https://pypi.org/project/pibooth/>`_:

.. code-block:: bash

        sudo pip3 install pibooth[dslr,printer]

.. hint:: If you don't have ``gPhoto2`` and/or ``CUPS`` installed (steps 5. and/
          or 6. skipped), remove printer or dslr under the ``[]``

Install developing version
--------------------------

.. warning:: Be aware that the code on the `master` branch may be unstable.

If you want to use an **unofficial version** of the ``pibooth`` application, you
need to work from a clone of this ``git`` repository. Replace the step 8. of the
:ref:`install` procedure by the following actions:

1. Clone from github :

.. code-block:: bash

    git clone https://github.com/pibooth/pibooth.git

2. Go in the cloned directory :

.. code-block:: bash

    cd pibooth

3. Install ``pibooth`` in editable mode :

.. code-block:: bash

    sudo pip3 install -e .[dslr,printer]

4. Start the application exactly in the same way as installed from pypi. All
   modifications performed in the cloned repository are taken into account when
   the application starts.

Naming
^^^^^^

Here is a small user guide and rules applied to develop ``pibooth``. They
will be updated as we go along.

1. **Conventions**

   The ``PEP8`` naming rules are applied.

2. **Capture / Picture / Image**

   In the code and the configuration file:

   - ``capture`` is used for variables related to a raw image from the camera.
   - ``picture`` is used for variables related to the final image which is
     a concatenation of capture(s) and text(s).
   - ``image`` shall be used for pictograms displayed in Pygame view or
     intermediate PIL/OpenCv objects.
