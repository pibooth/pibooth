.. _hooks:

Hooks specification
-------------------

The ``pibooth`` application provide a decorator to implement specific hooks.
Each hook have to be decorated has follow:

.. code-block:: python

    import pibooth

    @pibooth.hookimpl
    def pibooth_configure(cfg):
        ...

There is 2 different king of hooks:

- **State-independent hooks**: name is starting by **pibooth_** and permit to change the behavior
  of the pibooth standard features.
- **State dependant hooks** (see below): name is starting by **state_** and permit to customize
  actions done during states.

.. note:: Hooks specification defines all arguments that can be used by the hook
          implementation. But there is no need to put in the hook signature
          the arguments that are not used in the code.

.. automodule:: pibooth.plugins.hookspecs
   :members:
