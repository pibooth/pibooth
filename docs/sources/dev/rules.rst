Coding rules
------------

Here is a small user guide and rules applied to develop ``pibooth``. They
will be updated as we go along.

1. **Conventions**

The ``PEP8`` naming rules are applied, with a line length limit of 160
characters rather than 79 — that is what the continuous integration checks.

A few habits are shared by the whole code base. New code is expected to match
its surroundings rather than modernise them in passing:

- every module starts with the ``# -*- coding: utf-8 -*-`` header
- logging goes through ``from pibooth.utils import LOGGER``, with lazy
  arguments — ``LOGGER.info("Loaded %s", name)`` and not a pre-formatted
  string
- paths use ``import os.path as osp``
- strings are formatted with ``"{}".format(...)``

2. **Capture / Picture / Image**

In the code and the configuration file:

- ``capture`` is used for variables related to a raw image from the camera.
- ``picture`` is used for variables related to the final image which is
  a concatenation of capture(s) and text(s).
- ``image`` shall be used for pictograms displayed in Pygame view or
  intermediate PIL/OpenCv objects.

3. **Configuration options naming**

Option relative to a specific state shall have an name starting with the
state name.

Option relative to a timeout shall have an name ending with ``_delay```.

4. **Plugins naming**

The core plugins expose a ``name`` attribute of the form
``pibooth-core:<something>``. That name is what ``[GENERAL][plugins_disabled]``
matches against.

5. **Contributing a change**

- Keep a change focused. Do not turn a feature change into a repository-wide
  lint cleanup.
- Say plainly when a change could not be verified on real hardware, rather than
  implying it was tested.
