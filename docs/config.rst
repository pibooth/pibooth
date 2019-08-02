
Default configuration
---------------------

.. code-block:: ini

    [GENERAL]
    # User interface language ('de', 'en' or 'fr')
    language = en

    # Path to save pictures
    directory = ~/Pictures/pibooth

    # Cleanup the 'directory' before start
    clear_on_startup = True

    # Start pibooth at Raspberry Pi startup
    autostart = False

    # Show fail message and go back to wait state in case of exception
    failsafe = True

    [WINDOW]
    # The (width, height) of the display window or 'fullscreen'
    size = (800, 480)

    # Blinking background when picture is taken
    flash = True

    # Show arrows to indicate physical buttons ('bottom', 'top' or 'hidden')
    arrows = bottom

    # Apply horizontal offset to arrows position
    arrows_x_offset = 0

    # How long is the preview in seconds
    preview_delay = 3

    # Show a countdown timer during the preview
    preview_countdown = True

    # Stop the preview before taking the picture
    preview_stop_on_capture = False

    [PICTURE]
    # Possible choice(s) of captures numbers (numbers between 1 to 4 max)
    captures = (4, 1)

    # Orientation of the final image ('auto', 'portrait' or 'landscape')
    orientation = auto

    # Effect applied to the captures (a list of quoted names can be given)
    effect = none

    # Main text displayed
    footer_text1 = Footer 1

    # Secondary text displayed
    footer_text2 = Footer 2

    # Footer text RGB color
    text_color = (0, 0, 0)

    # Background RGB color or path to a background image
    bg_color = (255, 255, 255)

    # Font name/path/url to be used for footer texts (1 or 2 names/paths)
    fonts = ('Amatic-Bold', 'AmaticSC-Regular')

    [CAMERA]
    # Adjust for lighting issues, normal is 100 or 200 and dark is 800 max
    iso = 100

    # Flip horizontally the captured picture
    flip = False

    # Rotation of the camera (0, 90, 180 or 270)
    rotation = 0

    # Resolution for camera captures (preview will have same aspect ratio)
    resolution = (1934, 2464)

    [PRINTER]
    # Name of the printer defined in CUPS (or use the 'default' one)
    printer_name = default

    # How long is the print view in seconds (0 to skip it)
    printer_delay = 10

    # Maximum number of duplicate pages sent to the printer (avoid paper wast)
    max_duplicates = 3

    # Prints 1, 2, 3 or 4 picture copies per page
    nbr_copies = 1

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
