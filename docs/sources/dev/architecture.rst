Architecture
------------

``pibooth`` is a `pygame <https://www.pygame.org>`_ application driven by a state
machine, in which **every behaviour is implemented as a plugin** — including the
core features themselves. Since version 3, the main loop is an event loop: the
hardware buttons, the camera, the printer and the graphical elements communicate
through ``pygame`` events, and the slow operations (camera capture, picture
generation) run in background tasks.

Modules
^^^^^^^

::

    __main__.py         command line, plugins and configuration loading, GPIO fallback
    app.py              PiboothApplication: buttons/LEDs, camera, printer, StateMachine
     ├─ states.py       StateMachine: calls the state_<name>_* hooks
     ├─ evts.py         pibooth events (EVT_*) and helpers to find them
     ├─ tasks.py        AsyncTasksPool + AsyncTask: background work posting events
     ├─ plugins/        plugin manager and the 5 core plugins
     │   ├─ hookspecs.py       every hook available to plugins
     │   ├─ camera_plugin.py   preview and captures sequence
     │   ├─ picture_plugin.py  final picture assembly (in an AsyncTask)
     │   ├─ printer_plugin.py  CUPS printing
     │   ├─ view_plugin.py     states declaration, scenes and transitions
     │   └─ lights_plugin.py   GPIO LEDs
     ├─ config/         default.py (DEFAULT options) + parser.py (PiboothConfigParser)
     ├─ camera/         base.py + gphoto/opencv/hybrid drivers, auto-detected
     ├─ pictures/       factory.py (build the final picture), sizing.py
     ├─ view/           base.py (BaseWindow, BaseScene) and the two backends:
     │   ├─ pygame/     window.py (PygameWindow), menu.py (settings), sprites.py
     │   │   └─ scenes/  one module per state (wait.py, choose.py, ...)
     │   └─ nogui/      window.py: headless window for the --nogui mode
     ├─ language.py     translations, one section per language
     ├─ counters.py     persisted counters (JSON)
     ├─ printer.py      Printer: CUPS connection and notifications
     └─ utils.py        LOGGER, PollingTimer, logging helpers

The application entry point is ``pibooth.__main__:main``. The other ``pibooth-*``
commands live in ``pibooth/scripts/``.

Main loop
^^^^^^^^^

``PiboothApplication.exec()`` calls the ``pibooth_startup`` hook, activates the
``wait`` state and hands over to ``win.eventloop(app.update)``. On each iteration
the window:

1. collects the ``pygame`` events (user inputs, but also the ``EVT_*`` events
   posted by ``pibooth``, see below)
2. calls ``app.update(events)``, which runs the state machine — or, when the
   settings menu is shown, stops the preview and waits for the menu to close
3. updates its sprites according to the events and draws the ones that changed

::

    win.eventloop ──► app.update(events) ──► StateMachine.process(events)
                                                   │
                                                   ├─ state_<name>_do(cfg, app, win, events)
                                                   └─ state_<name>_validate(cfg, app, win, events)
                                                             │
                                             set_state(): state_<name>_exit ──► win.set_scene ──► state_<name>_enter

The state machine, the plugins and the drawing all run in the main thread. A
plugin must never block in a hook: a long operation goes in an
:py:class:`pibooth.tasks.AsyncTask` and the hook is called again on the next
iteration to check the result.

Events
^^^^^^

``pibooth/evts.py`` declares the events exchanged between the components, all
built on ``pygame.USEREVENT``:

======================================= ======================================================
Event                                   Posted by
======================================= ======================================================
``EVT_BUTTON_CAPTURE``                  the application, when the capture button is pressed
``EVT_BUTTON_PRINT``                    the application, when the print button is pressed
``EVT_BUTTON_SETTINGS``                 the application, both buttons held together
``EVT_PIBOOTH_CAPTURE``                 the view, a "capture" action on screen (touch or key)
``EVT_PIBOOTH_PRINT``                   the view, a "print" action on screen (touch or key)
``EVT_PIBOOTH_SETTINGS``                the view, the settings menu is shown or hidden
``EVT_PIBOOTH_CAM_PREVIEW``             the camera task, a new preview image is available
``EVT_PIBOOTH_CAM_CAPTURE``             the camera task, a capture is done
``EVT_PIBOOTH_PRINTER_UPDATE``          the printer, a CUPS notification was received
======================================= ======================================================

The ``events`` argument of the ``state_<name>_do`` and ``state_<name>_validate``
hooks is the list of events of the current iteration. Look for the one you need
with ``evts.find_event(events, evts.EVT_PIBOOTH_PRINT)`` or the ``evts.is_*_event``
helpers, and post your own with ``evts.post(event_type, **attributes)``.
Posting is the only thread-safe way to act on the view from a background task.

Asynchronous tasks
^^^^^^^^^^^^^^^^^^

``pibooth/tasks.py`` runs callables in a thread pool. An
:py:class:`pibooth.tasks.AsyncTask` starts as soon as it is created and, when
an ``event`` is given, posts it with ``result`` (or ``exception``) attributes
when the callable returns. With ``loop=True`` the callable is called again and
again until ``kill()``, which is how the camera preview works: the driver's
``get_preview_image()`` runs in a loop and every image reaches the view as an
``EVT_PIBOOTH_CAM_PREVIEW`` event.

``PiboothApplication`` owns the :py:class:`pibooth.tasks.AsyncTasksPool` and
stops every task on exit. The camera drivers and ``PicturePlugin`` are the
users of it in the core.

Camera drivers
^^^^^^^^^^^^^^

:py:class:`pibooth.camera.base.BaseCamera` implements the preview and capture
logic on top of the tasks: a driver only implements ``get_preview_image()``,
``get_capture_image()`` (both called from a background thread) and
``_process_capture()``. The ``capture()`` method never blocks: the capture is
reported by the ``EVT_PIBOOTH_CAM_CAPTURE`` event and the images are retrieved
with ``grab_captures()``.

``reset()`` is called by the camera plugin when the ``failsafe`` state is
entered, to reopen a connection left in a bad state by an error (gPhoto2
does it, other drivers have nothing to do). ``quit()`` is definitive.

Window and scenes
^^^^^^^^^^^^^^^^^

The view is a :py:class:`pibooth.view.base.BaseWindow` holding one
:py:class:`pibooth.view.base.BaseScene` per state. Two backends implement them:
``pygame`` for the real interface and ``nogui`` for the ``--nogui`` option,
which runs the whole application without a display (the states are then
switched by the keyboard in the console). Plugins access the window as ``win``
in the hooks and the current scene as ``win.scene``; a plugin should call only
the methods declared in ``pibooth/view/base.py``, so that it works with both
backends.

A ``pygame`` scene is a group of sprites (``pibooth/view/pygame/sprites.py``)
organized in layers, drawn from the bottom to the top:

* ``LAYER_BACKGROUND`` — background color or image, shared by all scenes
* ``LAYER_IMAGES`` — pictograms and layouts
* ``LAYER_TEXTS`` — texts
* ``LAYER_PICTURE`` — the main picture (camera preview, final picture), kept
  outside of the group for performance reasons
* ``LAYER_ARROWS`` — arrows or touch pictograms
* ``LAYER_STATUS`` — the status bar (printer queue, counters)

Sprites are ``DirtySprite`` objects: only the ones that changed are redrawn.
Any sprite of the images, texts and arrows layers can react to a click or a
touch through its ``on_pressed`` callback, which is how the scenes post the
``EVT_PIBOOTH_CAPTURE`` and ``EVT_PIBOOTH_PRINT`` events. Each scene computes
the position of its sprites in ``resize()``, according to the window size and
the ``[WINDOW][arrows]`` option.

The settings menu (``pibooth/view/pygame/menu.py``) is built with
`pygame-menu <https://pygame-menu.readthedocs.io>`_ from ``DEFAULT``: every
option with a menu label is editable there.

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
``state_<name>_enter`` of the new state, after the window switched to the scene
of the same name.

.. important:: A transition only ever happens because a ``_validate`` hook
               returned a state name. There is no other way to change state,
               and no state should be activated from anywhere else.

If an exception escapes a hook, the machine switches to the ``failsafe`` state
instead of propagating — unless the ``[GENERAL][debug]`` option is enabled, in
which case ``failsafe`` is removed and exceptions are raised. Keep that in mind
when a plugin seems to swallow errors.

The states themselves are declared by the ``pibooth_setup_states(cfg, win, machine)``
hook: ``ViewPlugin`` registers the eight standard states with their scenes, and
a plugin can add its own with ``machine.add_state(name, scene)`` or remove one
with ``machine.remove_state(name)``. A state added this way is driven by the
``state_<name>_*`` hooks like any other, declared with
``@pibooth.hookimpl(optionalhook=True)`` since they are not in ``hookspecs.py``
(see the custom state example in :doc:`/sources/plugins/examples`).

Plugins call order
^^^^^^^^^^^^^^^^^^

``PiboothPluginManager.load_all_plugins()`` registers, in this order:

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

Plugins can be enabled and disabled at runtime from the settings menu
(``app.enable_plugin()`` / ``app.disable_plugin()``): the manager keeps the
history of the hooks already called for each plugin, so that ``pibooth_configure``
and ``pibooth_startup`` are called when a plugin is enabled for the first time.

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

``pibooth/config/default.py`` is the single source of truth: the ``DEFAULT``
dictionary is filled by ``add_default_option()`` calls::

    add_default_option("SECTION", "option_name", default_value,
                       "comment written in pibooth.cfg",
                       "label in the graphical menu",   # optional
                       choices)                          # optional

The two last arguments are omitted for an option that exists only in the file
and is not exposed in the settings menu. Choices are strings, even for numeric
options; a string instead of a list of choices gives a free text input, and a
RGB tuple gives a color input.

The user file is **merged** with ``DEFAULT``, never overwritten: an option
missing from the user file falls back to its default. As a consequence, removing
or renaming an option silently changes the behaviour of existing installations.

Read options with the matching typed getter — ``gettyped``, ``gettuple``,
``getpath``, ``getint``, ``getfloat``, ``getboolean`` — rather than ``get`` and a
manual conversion.

An option that must apply without restarting has to be read in
``PiboothApplication._initialize()``, which runs at startup *and* every time the
settings menu is closed. Options read only in ``__init__`` require a restart.

Plugins declare their own options from the ``pibooth_configure`` hook with
``cfg.add_option(...)``, whose signature mirrors ``add_default_option()``
without the section.

.. note:: When ``DEFAULT`` changes, update ``docs/sources/config/default.cfg``
          as well: it is maintained by hand. It should stay identical to a
          freshly generated file, apart from its missing trailing newline::

              pibooth --reset /tmp/piboothcfg
              diff /tmp/piboothcfg/pibooth.cfg docs/sources/config/default.cfg

What cannot run outside a Raspberry Pi
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Most of the hardware-facing code cannot be exercised on a development machine:

* **GPIO** — ``__main__.py`` catches ``BadPinFactory`` and falls back to
  ``gpiozero``'s mock factory, logging *without physical GPIO*. Button and LED
  code runs but has no effect.
* **Pi Camera** — the ``picamera2`` driver of the 2.x versions is not ported
  to the asynchronous camera API yet: on a Raspberry Pi the camera has to be
  a webcam (OpenCV) or a DSLR (gPhoto2) for now.
* **DSLR and printing** — need real hardware, plus ``gphoto2`` and a CUPS
  server. Both are optional extras, and the corresponding modules guard their
  imports. The tests replace them by the mocks of ``tests/mocks/``.

``camera/__init__.py::find_camera()`` probes the available drivers; on a
development machine it usually resolves to ``CvCamera`` when a webcam is
present, and raises otherwise. The ``--nogui`` option and the
``SDL_VIDEODRIVER=dummy`` variable allow to run the application without any
display.
