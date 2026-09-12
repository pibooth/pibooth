Release for Pypi
----------------

1. Create a virtual environment and install the packaging tools in it:

   ::

        $ python3 -m venv /tmp/release-venv
        $ /tmp/release-venv/bin/pip install build twine

   .. note:: Installing them system-wide with ``sudo pip install`` fails on
             recent distributions, which mark the system Python as
             externally managed (:pep:`668`).

2. Update the version number in the ``pibooth/__init__.py`` file. It is the only
   place where the version is declared: ``setup.py`` imports it, and the
   ``download_url`` is built from it, so the git tag must later match it exactly.

3. Clean previous packages (avoid upload of an older package):

   ::

        $ rm -rf build/ dist/ pibooth.egg-info/

4. Generate the package:

   ::

        $ /tmp/release-venv/bin/python -m build --wheel .

   .. warning:: Do not use ``python setup.py bdist_wheel``. Direct invocation of
                ``setup.py`` is deprecated and now fails with recent versions of
                ``setuptools``.

5. Check the package integrity. This also validates that the reStructuredText
   ``long_description`` renders correctly, which PyPI rejects otherwise:

   ::

        $ /tmp/release-venv/bin/twine check dist/*

6. Check that the built package actually installs and starts, in a clean
   environment. This is what catches a broken dependency pin before the users
   do:

   ::

        $ python3 -m venv /tmp/install-check
        $ /tmp/install-check/bin/pip install dist/pibooth-*.whl
        $ SDL_VIDEODRIVER=dummy /tmp/install-check/bin/pibooth --reset /tmp/cfg-check

7. Upload the package on PyPI:

   ::

        $ /tmp/release-venv/bin/twine upload dist/*

   PyPI no longer accepts account passwords: authentication requires an API
   token, used as the password with ``__token__`` as the username. ``twine``
   prompts for it, or reads it from ``~/.pypirc`` or the ``TWINE_USERNAME`` /
   ``TWINE_PASSWORD`` environment variables.

   .. warning:: This step is irreversible: a version number can never be reused
                on PyPI.

8. Tag the release and push the tag, using exactly the version set in step 2:

   ::

        $ git tag <version>
        $ git push origin <version>
