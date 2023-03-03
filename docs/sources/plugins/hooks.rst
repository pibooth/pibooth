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

.. note:: Hooks specification defines all arguments that can be used by the hook
          implementation. But there is no need to put in the hook signature
          the arguments that are not used in the code.

.. automodule:: pibooth.plugins.hookspecs
   :members:
