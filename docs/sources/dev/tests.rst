Running the tests
-----------------

Install the test dependencies in the environment where ``pibooth`` was installed
in editable mode (see :ref:`install_developing_version`)::

    pip install pytest pytest-cov flake8 pylint
    pip install opencv-python

Then run the suite::

    SDL_VIDEODRIVER=dummy CAMERA_GPDRIVER=dummy CAMERA_CVDRIVER=dummy pytest

The variables matter, for different reasons:

``SDL_VIDEODRIVER=dummy``
    Makes ``pygame`` render offscreen. Without it, ``pygame`` tries to open a
    real display and the suite fails to collect. The window tests in
    ``tests/test_view.py`` also branch on this variable: with a real display,
    each scene stays on screen until ``ESC`` is pressed.

``CAMERA_GPDRIVER=dummy`` / ``CAMERA_CVDRIVER=dummy``
    Read by the camera fixtures of ``tests/conftest.py``. When set to ``dummy``,
    the gPhoto2 driver is replaced by the mock of ``tests/mocks/camera_drivers.py``
    and the OpenCV driver reads a still image instead of a webcam, so
    ``tests/test_camera.py`` runs without hardware. When a variable is absent,
    the fixture looks for a real camera and the tests are skipped if none is
    connected.

With all of them set and ``opencv-python`` installed, the whole suite passes on
a machine without any photobooth hardware, so a failure is a real one. The usual
cause of a mass failure is a missing ``opencv-python``, which takes out all of
``tests/test_factory.py``.

Fixtures live in ``tests/conftest.py``. The camera ones — ``camera_gp``,
``camera_cv`` and the hybrid variant — are the only ones that can touch real
hardware. The ``printer`` fixture replaces ``cups.Connection`` by a fake, so
``tests/test_printer.py`` does not need a CUPS server.

``tests/dslr_diag/`` holds ``pibooth-diag`` outputs contributed by users for
specific DSLR models. They are data files, not tests.

Linters
^^^^^^^

The continuous integration runs both, but only the first one can fail the
build::

    flake8 pibooth --count --select=E9,F63,F7,F82 --show-source --statistics
    flake8 pibooth --count --exit-zero --max-complexity=10 --max-line-length=160 --statistics
    pylint --rcfile=.pylintrc $(git ls-files 'pibooth/*.py' 'docs/*.py')

The second ``flake8`` invocation and ``pylint`` are informational: the code base
does not satisfy them today.

Starting the application
^^^^^^^^^^^^^^^^^^^^^^^^

To exercise the application itself without a photobooth::

    SDL_VIDEODRIVER=dummy pibooth --verbose --nolog /tmp/piboothcfg

``--verbose`` logs every state activation and its duration, which is the main
tool for debugging the state machine. ``--nolog`` avoids writing
``/tmp/pibooth.log``, and passing a throwaway configuration directory keeps
``~/.config/pibooth`` untouched.
