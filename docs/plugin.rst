
Extend ``pibooth`` functionalities
----------------------------------

The ``pibooth`` application is built on the top of
`pluggy <https://pluggy.readthedocs.io/en/latest/index.html>`_
that gives users the ability to extend or modify its behavior.

What is a plugin?
^^^^^^^^^^^^^^^^^

A plugin is a set of functions (called ``hooks``) defined in a python module
and participating to the ``pibooth`` execution when they are invoked.

The list of available ``hooks`` are defined in the file
`hookspecs.py <https://github.com/werdeil/pibooth/blob/master/pibooth/plugins/hookspecs.py>`_.
A plugin implements a subset of those functions.

Influencing states
^^^^^^^^^^^^^^^^^^

The ``pibooth`` application is built on the principle of states. Each state
is defined by a specific screen and possible actions available to the user.

The following states are defined:
 * ``wait``       : wait for starting a new capture sequence
 * ``choose``     : selection of the number of captures
 * ``chosen``     : confirm the number of captures
 * ``preview``    : show preview and countdown
 * ``capture``    : take a capture
 * ``processing`` : build the final picture
 * ``print``      : show preview and ask for printing
 * ``finish``     : thank before going back to wait state
 * ``failsafe``   : oops message when an exception occurs

.. image:: https://raw.githubusercontent.com/werdeil/pibooth/master/templates/state_sequence_details.png
    :align: center
    :alt: State sequence

There are four hooks defined for each state.

- ``state_<name>_enter``

  Invoked one time when the state is activating.

- ``state_<name>_do``

  Invoked in a loop until the state is switching to an other one.

- ``state_<name>_validate``

  Invoked in a loop, returns the name of the next state if all conditions
  are met (else return ``None``).

- ``state_<name>_exit``

  Invoked one time when the state is exiting.

.. note:: The hooks specification define all arguments that can be used by the
          hook, but there is no need to defined, in the function signature, the
          arguments not used in the code.

Example #1 : Hello from plugin
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``pibooth_hello.py``

.. code-block:: python

    import pibooth
    from pibooth.utils import LOGGER

    @pibooth.hookimpl
    def state_wait_enter():
        LOGGER.info("Hello from '%s' plugin", __name__)

Example #2 : Flash light on capture
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``pibooth_flash.py``

.. code-block:: python

    import pibooth
    from pibooth.controls.light import PtbLed

    FLASH = PtbLed(36) # GPIO configured as BOARD

    @pibooth.hookimpl
    def state_capture_enter():
        FLASH.switch_on()

    @pibooth.hookimpl
    def state_capture_exit():
        FLASH.switch_off()

Example #3 : Upload to FTP
^^^^^^^^^^^^^^^^^^^^^^^^^^

``pibooth_ftp.py``

.. code-block:: python

    import os
    from ftplib import FTP
    import pibooth


    @pibooth.hookimpl
    def state_processing_exit(app):
        ftp = FTP()
        ftp.set_debuglevel(0)
        ftp.connect("ftp.pibooth.org", 21)
        ftp.login("pibooth", "1h!gR4/opK")

        name = os.path.basename(app.previous_picture_file)

        with open(app.previous_picture_file, 'rb') as fp:
            ftp.storbinary('STOR {}'.format(name), fp, 1024)

        ftp.close()

Example #4 : Generate a QR-Code
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``pibooth_qrcode.py``

.. code-block:: python

    import os
    import qrcode
    import pygame

    import pibooth


    @pibooth.hookimpl
    def state_wait_enter(app, win):
        """Display the QR Code on the wait view.
        """
        if hasattr(app, 'previous_qr'):
            win_rect = win.get_rect()
            qr_rect = app.previous_qr.get_rect()
            win.surface.blit(app.previous_qr, (10, win_rect.height - qr_rect.height - 10))


    @pibooth.hookimpl
    def state_processing_exit(app):
        """Generate the QR Code and store it in the application.
        """
        qr = qrcode.QRCode(version=1,
                           error_correction=qrcode.constants.ERROR_CORRECT_L,
                           box_size=3,
                           border=1)

        name = os.path.basename(app.previous_picture_file)

        qr.add_data(os.path.join("www.pibooth.org/pictures", name))
        qr.make(fit=True)

        image = qr.make_image(fill_color="black", back_color="white").convert('RGB')
        app.previous_qr = pygame.image.fromstring(image.tobytes(), image.size, image.mode)


    @pibooth.hookimpl
    def state_print_enter(app, win):
        """Display the QR Code on the print view.
        """
        win_rect = win.get_rect()
        qr_rect = app.previous_qr.get_rect()
        win.surface.blit(app.previous_qr, (win_rect.width - qr_rect.width - 10,
                                           win_rect.height - qr_rect.height - 10))
