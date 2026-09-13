Running the tests
-----------------

Install the test dependencies in the environment where ``pibooth`` was installed
in editable mode (see :ref:`install_developing_version`)::

    pip install pytest pytest-cov flake8 pylint
    pip install opencv-python

Then run the suite::

    SDL_VIDEODRIVER=dummy CAM_VIDEODRIVER=dummy pytest

Both variables matter, for different reasons:

``SDL_VIDEODRIVER=dummy``
    Makes ``pygame`` render offscreen. Without it, ``pygame`` tries to open a
    real display and the suite fails to collect. ``tests/test_window.py`` also
    branches on this variable.

``CAM_VIDEODRIVER``
    Read only by ``tests/test_camera.py``, which skips every camera test when
    the variable is **present** — its value is irrelevant. Leave it unset only
    when a camera is actually connected.

With both set and ``opencv-python`` installed, the whole suite passes on a
machine without any photobooth hardware, so a failure is a real one. The usual
cause of a mass failure is a missing ``opencv-python``, which takes out all of
``tests/test_factory.py``.

Fixtures live in ``tests/conftest.py``. The camera ones — ``camera_rpi2``,
``camera_gp``, ``camera_cv`` and the hybrid variants — are those needing real
hardware.

``tests/test_camera_rpi2.py`` is the exception: it stubs the ``picamera2``
library, so the preview and capture processing of ``Rpi2Camera`` is covered on
any machine.

``tests/dslr_diag/`` holds ``pibooth-diag`` outputs contributed by users for
specific DSLR models. They are data files, not tests.

The continuous integration runs the suite with ``--cov-fail-under``: the job
fails when the total coverage drops under the floor set in
``.github/workflows/tests.yml``. Raise the floor when the coverage improves.

Linters
^^^^^^^

The continuous integration runs both, but only the first one can fail the
build::

    flake8 pibooth --count --select=E9,F63,F7,F82 --show-source --statistics
    flake8 pibooth --count --exit-zero --max-complexity=10 --max-line-length=160 --statistics
    pylint $(git ls-files '*.py')

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
