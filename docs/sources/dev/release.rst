Release for Pypi
----------------

1. Install packaging libraries:

   ::

        $ sudo pip install setuptools wheel twine

2. Update the version number in the ``pibooth/__init__.py`` file.

3. Check the rendering of the README by generating the HTML page:

   ::

        $ python setup.py --long-description | rst2html.py > output.html

4. Clean previous packages (avoid upload of older package):

   ::

        $ rm -rf build/ dist/

5. Generate the package:

   ::

        $ python setup.py bdist_wheel

6. Check the package integrity:

   ::

        $ twine check dist/*

7. Upload the package on Pypi (replace XXXXXX by username and password of your
   Pypi account):

   ::

        $ twine upload -u XXXXXX -p XXXXXX dist/*
