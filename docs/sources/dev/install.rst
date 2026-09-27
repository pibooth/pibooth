.. _install_developing_version:

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

3. Create a virtual environment and install ``pibooth`` in editable mode in it:

.. code-block:: bash

    python3 -m venv --system-site-packages .venv
    .venv/bin/pip install -e .[dslr,printer]

.. note:: Installing with ``sudo pip3 install -e .`` no longer works: since
          Bookworm the system Python is *externally managed* (:pep:`668`) and
          ``pip`` refuses to write into it. ``--system-site-packages`` keeps the
          libraries installed with ``apt`` — ``python3-opencv``,
          ``python3-picamera2``, the GPIO ones — visible from the virtual
          environment.

4. Start the application with ``.venv/bin/pibooth``, exactly in the same way as
   installed from pypi. All modifications performed in the cloned repository are
   taken into account when the application starts.
