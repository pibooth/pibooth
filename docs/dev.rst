

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

    $ sudo pip3 install -e .[dslr,printer]

4. Start the application exactly in the same way as installed from pypi. All modifications performed
   in the cloned repository are taken into account when the application starts.

Developing rules
----------------

Here is a small user guide and rules applied to develop ``pibooth``. They
will be updated as we go along.

Naming
^^^^^^

1. **Conventions**

   The ``PEP8`` naming rules are applied.

2. **Capture / Picture / Image**

   In the code and the configuration file:

   - ``capture`` is used for variables related to a raw image from the camera.
   - ``picture`` is used for variables related to the final image which is
     a concatenation of capture(s) and text(s).
   - ``image`` shall be used for pictograms displayed in Pygame view or
     intermediate PIL/OpenCv objects.
