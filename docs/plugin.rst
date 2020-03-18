
Extend ``pibooth`` functionalities
----------------------------------

The ``pibooth`` application is built on the top of
`pluggy <https://pluggy.readthedocs.io/en/latest/index.html>`_
that gives users the ability to extend or modify its behavior.

Hook specification
^^^^^^^^^^^^^^^^^^

A plugin is a set of functions (called ``hooks``) defined in a python module
and participating to the ``pibooth`` execution when they are invoked.

The list of available ``hooks`` are defined in the file are defined in the file
`hookspecs.py <https://github.com/werdeil/pibooth/blob/master/pibooth/plugins/hookspecs.py>`_.

A plugin implements a subset of the functions defined in this specification.

Influencing states
^^^^^^^^^^^^^^^^^^

The ``pibooth`` application is built on the principle of states. Each state
is defined by a specific screen and possible actions available to the user.

The following states are defined:
 * ``wait``       : wait for starting a new sequence
 * ``choose``     : selection of the number of captures
 * ``chosen``     : confirm the number of captures
 * ``capture``    : take captures
 * ``processing`` : build the final picture
 * ``print``      : ask for printing
 * ``finish``     : thank before going back to wait state
 * ``failsafe``   : oops message when an exception occurs

There are four hooks defined for each state. The ``enter`` hook is invoked one
time when the state is activated. The ``do`` one is invoked in a loop until
the state is switching to an other one. The ``validate``, also invoked in a
loop, returns the name  of the next state. And finally the ``exit`` hook is
invoked one time when the state is exited.

Example #1 : blabla
^^^^^^^^^^^^^^^^^^^

``pibooth_blabla.py``

.. code-block:: python

    import pibooth
