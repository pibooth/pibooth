
Default configuration
---------------------

.. code-block:: ini

    [GENERAL]
    # User interface language: 'de', 'en', 'es', 'fr', 'hu' or 'nl'
    language = en

    # Path to save pictures
    directory = ~/Pictures/pibooth

    # Cleanup the 'directory' before start
    clear_on_startup = False

    # Start pibooth at Raspberry Pi startup
    autostart = False

    # In debug mode, exceptions are not caught, logs are more verbose
    debug = False

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

    # How long is displayed the final image in seconds before being hidden (-1 if never hidden)
    final_image_delay = -1

    # Show arrows to indicate physical buttons: 'bottom', 'top' or 'hidden'
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

    # Main text displayed
    footer_text1 = Footer 1

    # Secondary text displayed
    footer_text2 = Footer 2

    # RGB colors used for footer texts (list of tuple accepted)
    text_colors = (0, 0, 0)

    # Fonts name or file path used for footer texts (list of quoted names accepted)
    text_fonts = ('Amatic-Bold', 'AmaticSC-Regular')

    # Alignments used for footer texts: 'left', 'center' or 'right' (list of quoted names accepted)
    text_alignments = center

    # Overlay path (PNG file) with same aspect ratio than final picture (list of path accepted)
    overlays =

    # Background RGB color or image path (list of tuple or path accepted)
    backgrounds = (255, 255, 255)

    [CAMERA]
    # Adjust for lighting issues, normal is 100 or 200 and dark is 800 max
    iso = 100

    # Flip horizontally the capture
    flip = False

    # Rotation of the camera: 0, 90, 180 or 270
    rotation = 0

    # Resolution for camera captures (preview will have same aspect ratio)
    resolution = (1934, 2464)

    # Delete captures from camera internal memory (when applicable)
    delete_internal_memory = False

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
    # How long to debounce the hardware buttons in seconds
    debounce_delay = 0.5

    # Physical GPIO IN pin to take a picture
    picture_btn_pin = 11

    # Physical GPIO OUT pin to light a LED when picture button is pressed
    picture_led_pin = 7

    # Physical GPIO IN pin to print a picture
    print_btn_pin = 13

    # Physical GPIO OUT pin to light a LED when print button is pressed
    print_led_pin = 15

    # Physical GPIO OUT pin to light a LED at pibooth startup
    startup_led_pin = 29

    # Physical GPIO OUT pin to light a LED during preview
    preview_led_pin = 31
