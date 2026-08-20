Architecture
------------

``pibooth`` is a `pygame <https://www.pygame.org>`_ application driven by a state
machine, in which **every behaviour is implemented as a plugin** — including the
core features themselves.

Modules
^^^^^^^

::

    booth.py            PiApplication + main_loop(): pygame event loop, GPIO buttons/LEDs
     ├─ states.py       StateMachine: calls the state_<name>_* hooks
     ├─ plugins/        plugin manager and the 5 core plugins
     │   ├─ hookspecs.py       every hook available to plugins
     │   ├─ camera_plugin.py   captures sequence
     │   ├─ picture_plugin.py  final picture assembly
     │   ├─ printer_plugin.py  CUPS printing
     │   ├─ view_plugin.py     screens and transitions
     │   └─ lights_plugin.py   GPIO LEDs
     ├─ config/         parser.py (DEFAULT) + menu.py (graphical settings)
     ├─ camera/         base.py + rpi2/gphoto/opencv/hybrid backends, auto-detected
     ├─ pictures/       factory.py (build the final picture), sizing.py, pool.py
     ├─ view/           window.py (PiWindow) + background.py (one class per screen)
     ├─ language.py     translations, one section per language
     ├─ counters.py     persisted counters
     └─ utils.py        LOGGER, PoolingTimer, logging helpers

The application entry point is ``pibooth.booth:main``. The other ``pibooth-*``
commands live in ``pibooth/scripts/``.

State machine
^^^^^^^^^^^^^

The list of states and the four hooks defined for each of them are described in
:ref:`extend_pibooth_functionalities`. What matters here is how
``StateMachine`` (``pibooth/states.py``) uses them.

On each iteration of the main loop, for the active state, it calls:

1. ``state_<name>_do(cfg, app, win, events)``
2. ``state_<name>_validate(cfg, app, win, events)``, which returns the name of
   the next state or ``None``

and, when a transition happens, ``state_<name>_exit`` then the
``state_<name>_enter`` of the new state.

.. important:: A transition only ever happens because a ``_validate`` hook
               returned a state name. There is no other way to change state,
               and no state should be activated from anywhere else.

If an exception escapes a hook, the machine switches to the ``failsafe`` state
instead of propagating — unless the ``[GENERAL][debug]`` option is enabled, in
which case ``failsafe`` is removed and exceptions are raised. Keep that in mind
when a plugin seems to swallow errors.

Plugins call order
^^^^^^^^^^^^^^^^^^

``PiPluginManager.load_all_plugins()`` registers, in this order:

1. plugins declared through ``setuptools`` entry points (installed with ``pip``)
2. the plugins listed in ``[GENERAL][plugins]``
3. the five core plugins

Hooks are called in **LIFO order**: the last plugin registered is called first.
The core plugins are therefore registered last **on purpose**, so that they run
before any external plugin. The list in ``pibooth/plugins/__init__.py`` is written
in *registration* order (``LightsPlugin`` first, ``CameraPlugin`` last), which is
the reverse of the *call* order — ``CameraPlugin`` is called first and
``LightsPlugin`` last. Reordering that list changes the runtime behaviour.

.. warning:: This has a consequence that surprises plugin authors. The
             ``state_<name>_validate`` hooks are declared ``firstresult=True``,
             so the **first** non-``None`` result wins and the remaining
             implementations are not even called. Since core plugins run first,
             an external plugin cannot prevent a transition that a core plugin
             has already decided.

             Returning ``None`` from ``state_finish_validate`` for instance does
             not keep the application on the finish screen: ``ViewPlugin`` has
             already returned ``'wait'`` once its timer expired.

Right after loading, ``check_pending()`` runs: any hook implementation whose
name is not declared in ``hookspecs.py`` raises at startup, unless it is
decorated with ``@pibooth.hookimpl(optionalhook=True)``.

Hooks are a public API
^^^^^^^^^^^^^^^^^^^^^^

``pibooth/plugins/hookspecs.py`` is consumed by third-party plugins published on
PyPI, and its docstrings are rendered as :ref:`hooks`.

* adding a hook, or adding a parameter to an existing one, is backward
  compatible — implementations only declare the arguments they use
* renaming a hook, removing one, or removing a parameter breaks every installed
  plugin that uses it

Configuration
^^^^^^^^^^^^^

``pibooth/config/parser.py::DEFAULT`` is the single source of truth. Each option
is a 4-tuple::

    ("option_name", (default_value,
                     "comment written in pibooth.cfg",
                     "label in the graphical menu" or None,
                     choices or None))

The 3rd and 4th items are ``None`` together for an option that exists only in
the file and is not exposed in the settings menu. Choices are strings, even for
numeric options.

The user file is **merged** with ``DEFAULT``, never overwritten: an option
missing from the user file falls back to its default. As a consequence, removing
or renaming an option silently changes the behaviour of existing installations.

Read options with the matching typed getter — ``gettyped``, ``gettuple``,
``getpath``, ``getint``, ``getfloat``, ``getboolean`` — rather than ``get`` and a
manual conversion.

An option that must apply without restarting has to be read in
``PiApplication._initialize()``, which runs at startup *and* every time the
settings menu is closed. Options read only in ``__init__`` require a restart.

Plugins declare their own options from the ``pibooth_configure`` hook with
``cfg.add_option(...)``, whose signature mirrors the tuple above.

.. note:: When ``DEFAULT`` changes, update ``docs/sources/config/default.cfg``
          as well: it is maintained by hand. It should stay identical to a
          freshly generated file, apart from its missing trailing newline::

              pibooth --reset /tmp/piboothcfg
              diff /tmp/piboothcfg/pibooth.cfg docs/sources/config/default.cfg

What cannot run outside a Raspberry Pi
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Most of the hardware-facing code cannot be exercised on a development machine:

* **GPIO** — ``booth.py`` catches ``BadPinFactory`` and falls back to
  ``gpiozero``'s mock factory, logging *without physical GPIO*. Button and LED
  code runs but has no effect.
* **Pi Camera** — ``picamera2`` and its ``libcamera`` binding come from ``apt``
  on Raspberry Pi OS and are not installable on a development machine, so
  ``Rpi2Camera`` and ``HybridRpi2Camera`` are unreachable elsewhere.
* **DSLR and printing** — need real hardware, plus ``gphoto2`` and a CUPS
  server. Both are optional extras, and the corresponding modules guard their
  imports.

``camera/__init__.py::find_camera()`` probes the available backends; on a
development machine it usually resolves to ``CvCamera`` when a webcam is
present, and raises otherwise.
