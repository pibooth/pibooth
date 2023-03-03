Coding rules
------------

Here is a small user guide and rules applied to develop ``pibooth``. They
will be updated as we go along.

1. **Conventions**

The ``PEP8`` naming rules are applied.

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
