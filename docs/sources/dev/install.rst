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

3. Install ``pibooth`` in editable mode :

.. code-block:: bash

    sudo pip3 install -e .[dslr,printer]

4. Start the application exactly in the same way as installed from pypi. All
   modifications performed in the cloned repository are taken into account when
   the application starts.
