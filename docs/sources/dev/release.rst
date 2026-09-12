Release for Pypi
----------------

The package is built and uploaded to PyPI by the ``tests`` GitHub workflow
(``.github/workflows/tests.yml``) when a version tag is pushed. The upload
uses PyPI *trusted publishing*: PyPI trusts the OpenID Connect token issued
by GitHub to the ``publish`` job, so no API token or password is stored
anywhere.

Release from GitHub Actions
^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. Update the version number in the ``pibooth/__init__.py`` file. It is the only
   place where the version is declared: ``setup.py`` imports it, and the
   ``download_url`` is built from it, so the git tag must match it exactly.

2. Merge the pull request carrying the new version into ``master``. The
   ``build`` and ``package`` jobs of the workflow run on the pull request: they
   run the tests, build the source distribution and the wheel, check them with
   ``twine`` and install the wheel in a clean environment.

3. Tag the merge commit with exactly the version set in step 1 and push the
   tag:

   ::

        $ git checkout master
        $ git pull
        $ git tag <version>
        $ git push origin <version>

   The workflow runs again on the tag. Once the ``build`` and ``package`` jobs
   are green, the ``publish`` job checks that the packaged version is the tag
   name and waits for a manual approval.

4. Approve the deployment: open the workflow run in the *Actions* tab of the
   repository, click on *Review deployments*, tick the ``pypi`` environment and
   *Approve and deploy*. The job then uploads ``dist/*`` to PyPI.

   .. warning:: This step is irreversible: a version number can never be reused
                on PyPI. If the run fails after the upload, or if something is
                wrong with the release, bump the version and start again.

5. Write the release notes on GitHub (*Releases* → *Draft a new release*, pick
   the pushed tag).

One-time configuration
^^^^^^^^^^^^^^^^^^^^^^

Both settings can only be done by a maintainer of the project, the ``publish``
job fails without them:

* On PyPI, in the ``pibooth`` project → *Manage* → *Publishing*, add a GitHub
  *trusted publisher* with owner ``pibooth``, repository ``pibooth``, workflow
  file name ``tests.yml`` and environment name ``pypi``.

* On GitHub, in *Settings* → *Environments*, create the ``pypi`` environment
  and enable *Required reviewers* with the maintainers allowed to approve a
  release. This is what makes the ``publish`` job wait for the approval of
  step 4.

Manual release (fallback)
^^^^^^^^^^^^^^^^^^^^^^^^^

If the workflow can not be used, the package can still be built and uploaded
from a development machine. It requires a PyPI API token.

1. Create a virtual environment and install the packaging tools in it:

   ::

        $ python3 -m venv /tmp/release-venv
        $ /tmp/release-venv/bin/pip install build twine

   .. note:: Installing them system-wide with ``sudo pip install`` fails on
             recent distributions, which mark the system Python as
             externally managed (:pep:`668`).

2. Update the version number in the ``pibooth/__init__.py`` file, as in the
   automated procedure.

3. Clean previous packages (avoid upload of an older package):

   ::

        $ rm -rf build/ dist/ pibooth.egg-info/

4. Generate the package:

   ::

        $ /tmp/release-venv/bin/python -m build .

   .. warning:: Do not use ``python setup.py bdist_wheel``. Direct invocation of
                ``setup.py`` is deprecated and now fails with recent versions of
                ``setuptools``.

5. Check the package integrity. This also validates that the reStructuredText
   ``long_description`` renders correctly, which PyPI rejects otherwise:

   ::

        $ /tmp/release-venv/bin/twine check --strict dist/*

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

   .. note:: Pushing the tag triggers the ``publish`` job of the workflow. As
             the version is already on PyPI, the upload is refused and the job
             fails: this is expected, the release is done.
