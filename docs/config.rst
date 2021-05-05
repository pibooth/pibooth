
Default configuration
---------------------

.. note:: Relative path (path which doesn't start by a ``/``) can be used. In this
          case, the absolute path is computed from the configuration file location.

.. code-block:: ini

    [GENERAL]
    # User interface language: 'de', 'dk', 'en', 'es', 'fr', 'hu', 'nl' or 'no'
    language = en

    # Path to save pictures (list of quoted paths accepted)
    directory = ~/Pictures/pibooth

    # Start pibooth at Raspberry Pi startup
    autostart = False

    # In debug mode, exceptions are not caught, logs are more verbose, pictures are cleared at startup
    debug = False

    # Path to custom plugin(s) not installed with pip (list of quoted paths accepted)
    plugins =

    # Enable a virtual keyboard in the settings interface
    vkeyboard = False

    [WINDOW]
    # The (width, height) of the display window or 'fullscreen'
    size = (800, 480)

    # Background RGB color or image path
    background = (0, 0, 0)

    # Text RGB color
    text_color = (255, 255, 255)

    # Blinking background when a capture is taken
    flash = True

    # Animate the last taken picture by displaying captures one by one
    animate = False

    # How long is displayed the capture in seconds before switching to the next one
    animate_delay = 0.2

    # How long is displayed the final picture in seconds before being hidden (-1 if never hidden)
    final_image_delay = -1

    # Show arrows to indicate physical buttons: 'bottom', 'top', 'hidden' or 'touchscreen'
    arrows = bottom

    # Apply horizontal offset to arrows position
    arrows_x_offset = 0

    # How long is the preview in seconds
    preview_delay = 3

    # Show a countdown timer during the preview
    preview_countdown = True

    # Stop the preview before taking the capture
    preview_stop_on_capture = False

    [PICTURE]
    # Orientation of the final picture: 'auto', 'portrait' or 'landscape'
    orientation = auto

    # Possible choice(s) of captures numbers (numbers between 1 to 4)
    captures = (4, 1)

    # Effect applied to the captures (list of quoted names accepted)
    captures_effects = none

    # Crop each capture border in order to fit the paper size
    captures_cropping = False

    # Thick (in pixels) between captures and picture borders/texts
    margin_thick = 100

    # Main text displayed
    footer_text1 = Footer 1

    # Secondary text displayed
    footer_text2 = Footer 2

    # RGB colors used for footer texts (list of tuples accepted)
    text_colors = (0, 0, 0)

    # Fonts name or file path used for footer texts (list of quoted names accepted)
    text_fonts = ('Amatic-Bold', 'AmaticSC-Regular')

    # Alignments used for footer texts: 'left', 'center' or 'right' (list of quoted names accepted)
    text_alignments = center

    # Overlay path (PNG file) with same aspect ratio than final picture (list of quoted paths accepted)
    overlays =

    # Background RGB color or image path (list of tuples or quoted paths accepted)
    backgrounds = (255, 255, 255)

    [CAMERA]
    # Adjust ISO for lighting issues, can be different for preview and capture (list of integer accepted)
    iso = 100

    # Flip horizontally the capture
    flip = False

    # Rotation of the camera: 0, 90, 180 or 270
    rotation = 0

    # Resolution for camera captures (preview will have same aspect ratio)
    resolution = (1934, 2464)

    # Delete captures from camera internal memory (when applicable)
    delete_internal_memory = False

    # Force preview to be captured with gPhoto2 for some DSLR camera
    force_gphoto2_for_preview = False

    # Configure the camera device address for preview and capture
    camera_device_address = /dev/video0

    [PRINTER]
    # Name of the printer defined in CUPS (or use the 'default' one)
    printer_name = default

    # How long is the print view in seconds (0 to skip it)
    printer_delay = 10

    # Maximum number of printed pages before warning on paper/ink levels (-1 = infinite)
    max_pages = -1

    # Maximum number of duplicate pages sent to the printer (avoid paper waste)
    max_duplicates = 3

    # Print 1, 2, 3 or 4 picture copies per page
    pictures_per_page = 1

    [CONTROLS]
    # How long to press a single hardware button in seconds
    debounce_delay = 0.3

    # How long to press multiple hardware buttons in seconds
    multi_press_delay = 0.5

    # Physical GPIO IN pin to take a picture
    picture_btn_pin = 11

    # Physical GPIO OUT pin to light a LED when picture button is pressed
    picture_led_pin = 7

    # Physical GPIO IN pin to print a picture
    print_btn_pin = 13

    # Physical GPIO OUT pin to light a LED when print button is pressed
    print_led_pin = 15
