

Install developing version
--------------------------

If you want to use an **unofficial version** of the ``pibooth`` application, you need to work from
a clone of this ``git`` repository. Replace the step 7. of the `Install <https://github.com/werdeil/pibooth/blob/master/README.rst#Install>`_ procedure by the
following actions:

1. Clone from github ::

    $ git clone https://github.com/werdeil/pibooth.git

2. Go in the cloned directory ::

    $ cd pibooth

3. Install ``pibooth`` in editable mode ::

    $ sudo pip3 install -e .

4. Start the application exactly in the same way as installed from pypi. All modifications performed
   in the cloned repository are taken into account when the application starts.
