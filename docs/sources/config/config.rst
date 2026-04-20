Default configuration
---------------------

**Relative paths:**

Relative path (path which doesn't start by a ``/``) can be used. In this
case, the path is considered starting from the configuration file location.

**List of elements:**

Option with mention ``list of quoted ...`` indicated means that a list of 2 or
more elements can be provided. A list starts and finishes with parenthesis
``(...)``. Each element is separated by a comma ``,``.

:download:`pibooth.cfg<default.cfg>`

.. literalinclude:: ./default.cfg
    :language: ini

Customizing per layout
----------------------

When multiple capture layouts are enabled (e.g. ``captures = (4, 3, 2, 1)``),
you can provide a different background, overlay, effect and text color for each
layout. The order matches the ``captures`` tuple.

**Orientation behavior:**

With ``orientation = auto``, pibooth automatically picks the best orientation
based on the number of captures:

.. list-table::
   :header-rows: 1

   * - Captures
     - Final image orientation
   * - 1 photo
     - Same as camera (typically portrait)
   * - 4 photos
     - Same as camera (typically portrait)
   * - 2 photos
     - Inverted (landscape if camera is portrait)
   * - 3 photos
     - Inverted (landscape if camera is portrait)

**Example: different background and overlay per layout**

.. code-block:: ini

   [PICTURE]
   captures = (4, 3, 2, 1)
   orientation = auto

   # One background per layout (in same order as captures)
   # Portrait layouts: 2400x3600px, Landscape layouts: 3600x2400px
   backgrounds = ('bg_4photos.jpg', 'bg_3photos.jpg', 'bg_2photos.jpg', 'bg_1photo.jpg')

   # Overlays (PNG with alpha channel), empty string to skip
   overlays = ('overlay_4.png', '', '', 'overlay_1.png')

   # Different effects per capture
   captures_effects = ('none', 'blur', 'none', 'sharpen')

   # Different text colors per layout
   text_colors = ((255, 255, 255), (0, 0, 0), (0, 0, 0), (255, 255, 255))

You can also mix image paths with RGB color tuples for backgrounds:

.. code-block:: ini

   # Photo 4: custom image, Photo 3: white, Photo 2: image, Photo 1: black
   backgrounds = ('bg_4photos.jpg', (255, 255, 255), 'bg_2photos.jpg', (0, 0, 0))

**Preparing overlay files:**

- Format: PNG 32-bit with alpha channel (RGBA)
- Transparent zones (alpha = 0) let the photos show through
- Decorative elements (frames, logos) should be opaque
- Match the final image dimensions for best quality:
  portrait = 2400x3600px, landscape = 3600x2400px (at default 600 DPI, 4x6 paper)
- Keep file size under 5 MB for Raspberry Pi performance

**Preparing background files:**

- Format: JPG (no transparency needed), quality 85-90%
- Same dimensions as overlay files
- Will be cropped to fit if aspect ratio differs
