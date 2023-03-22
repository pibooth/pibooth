# -*- coding: utf-8 -*-

import itertools
from collections import OrderedDict as odict
from pibooth import language


DEFAULT = odict()


def values_list_repr(values):
    """Concatenate a list of values to a readable string.
    """
    return "'{}' or '{}'".format("', '".join([str(i) for i in values[:-1]]), values[-1])


def add_default_option(section, option, default, description, menu_name=None, menu_choices=None):
    """Add an option to the default configuration.
    """
    DEFAULT.setdefault(section, odict())[option] = (default, description, menu_name, menu_choices)


# --- GENERAL ------------------------------------------------------------------

add_default_option("GENERAL", "language", "en",
                   f"User interface language: {values_list_repr(language.get_supported_languages())}",
                   "UI language", language.get_supported_languages())

add_default_option("GENERAL", "directory", "~/Pictures/pibooth",
                   "Path to save pictures (list of quoted paths accepted)")

add_default_option("GENERAL", "autostart", False,
                   "Start pibooth at Raspberry Pi startup",
                   "Auto-start", ['True', 'False'])

add_default_option("GENERAL", "autostart_delay", 0,
                   "How long to wait in second before start pibooth at Raspberry Pi startup",
                   "Auto-start delay", [str(i) for i in range(0, 121, 5)])

add_default_option("GENERAL", "debug", False,
                   "In debug mode, exceptions will stop pibooth, logs are more verbose, image placeholders at screen",
                   "Debug mode", ['True', 'False'])

add_default_option("GENERAL", "plugins", '',
                   "Path to custom plugin(s) not installed with pip (list of quoted paths accepted)")

add_default_option("GENERAL", "plugins_disabled", '',
                   "Plugin names to be disabled after startup (list of quoted names accepted)")

add_default_option("GENERAL", "vkeyboard", False,
                   "Enable a virtual keyboard in the settings interface",
                   "Virtual keyboard", ['True', 'False'])

# --- WINDOW -------------------------------------------------------------------

add_default_option("WINDOW", "size", (800, 480),
                   "The (width, height) of the display window or 'fullscreen'",
                   'Startup size', ['(800, 480)', 'fullscreen'])

add_default_option("WINDOW", "background", (0, 0, 0),
                   "Background RGB color or image path")

add_default_option("WINDOW", "font", 'Amatic-Bold',
                   "Font name or file path used for app texts")

add_default_option("WINDOW", "text_color", (255, 255, 255),
                   "Text RGB color",
                   "Text RGB color", (255, 255, 255))

add_default_option("WINDOW", "flash", True,
                   "Blinking background when a capture is taken",
                   "Flash on capture", ['True', 'False'])

add_default_option("WINDOW", "animate", False,
                   "Animate the last taken picture by displaying captures one by one",
                   "Animated picture", ['True', 'False'])

add_default_option("WINDOW", "animate_delay", 0.2,
                   "How long is displayed the capture in seconds before switching to the next one")

add_default_option("WINDOW", "wait_picture_delay", -1,
                   "On 'wait' state: how long is displayed the final picture in seconds before being hidden (-1 if never hidden)",
                   "Wait picture display time", ['-1'] + [str(i) for i in range(0, 121, 5)])

add_default_option("WINDOW", "chosen_delay", 4,
                   "How long is displayed the 'chosen' state:  (0 if never shown)",
                   "Chosen layout display time", [str(i) for i in range(0, 10)])

add_default_option("WINDOW", "finish_picture_delay", 0,
                   "On 'finish' state: how long is displayed the final picture in seconds (0 if never shown)",
                   "Finish picture display time", [str(i) for i in range(0, 121, 5)])

add_default_option("WINDOW", "arrows", 'bottom',
                   "Show arrows to indicate physical buttons: 'bottom', 'top', 'hidden' or 'touchscreen'",
                   "Show button arrows", ['bottom', 'top', 'hidden', 'touchscreen'])

add_default_option("WINDOW", "arrows_x_offset", 0,
                   "Apply horizontal offset to arrows position")

add_default_option("WINDOW", "preview_delay", 3,
                   "How long is the preview in seconds (0 if never shown)",
                   "Preview delay", [str(i) for i in range(0, 21)])

add_default_option("WINDOW", "preview_countdown", True,
                   "Show a countdown timer during the preview",
                   "Preview countdown", ['True', 'False'])

# --- PICTURE ------------------------------------------------------------------

add_default_option("PICTURE", "orientation", 'auto',
                   "Orientation of the final picture: 'auto', 'portrait' or 'landscape'",
                   "Orientation", ['auto', 'portrait', 'landscape'])

add_default_option("PICTURE", "captures", (1, 2, 3, 4),
                   "Possible choice(s) of captures numbers (numbers between 1 to 4)",
                   "Number of captures", ['(1, 2, 3, 4)', '1', '2', '3', '4'] + [str(val) for val in itertools.permutations(range(1, 5), 2)])

add_default_option("PICTURE", "captures_effects", 'none',
                   "Effect applied to the captures (list of quoted names accepted)")

add_default_option("PICTURE", "captures_cropping", False,
                   "Crop each capture border in order to fit the paper size",
                   "Crop captures", ['True', 'False'])

add_default_option("PICTURE", "margin_thick", 100,
                   "Thick (in pixels) between captures and picture borders/texts",
                   "Borders width", [str(i) for i in range(0, 210, 10)])

add_default_option("PICTURE", "footer_text1", "Footer 1",
                   "Main text displayed",
                   "Title", "")

add_default_option("PICTURE", "footer_text2", "Footer 2",
                   "Secondary text displayed",
                   "Sub-title", "")

add_default_option("PICTURE", "text_colors", (0, 0, 0),
                   "RGB colors used for footer texts (list of tuples accepted)")

add_default_option("PICTURE", "text_fonts", ('Amatic-Bold', 'AmaticSC-Regular'),
                   "Fonts name or file path used for footer texts (list of quoted names accepted)")

add_default_option("PICTURE", "text_alignments", 'center',
                   "Alignments used for footer texts: 'left', 'center' or 'right' (list of quoted names accepted)")

add_default_option("PICTURE", "overlays", '',
                   "Overlay path (PNG file) with same aspect ratio than final picture (list of quoted paths accepted)")

add_default_option("PICTURE", "backgrounds", (255, 255, 255),
                   "Background RGB color or image path (list of tuples or quoted paths accepted)")

# --- CAMERA -------------------------------------------------------------------

add_default_option("CAMERA", "iso", 100,
                   "Adjust ISO for lighting issues, can be different for preview and capture (list of integers accepted)")

add_default_option("CAMERA", "flip", False,
                   "Flip horizontally the capture")

add_default_option("CAMERA", "rotation", 0,
                   "Rotation of the camera: 0, 90, 180 or 270, can be different for preview and capture (list of integers accepted)")

add_default_option("CAMERA", "resolution", (1934, 2464),
                   "Resolution for camera captures (preview will have same aspect ratio)")

add_default_option("CAMERA", "delete_internal_memory", False,
                   "Delete captures from camera internal memory (when applicable)")

# --- PRINTER ------------------------------------------------------------------

add_default_option("PRINTER", "printer_name", "default",
                   "Name of the printer defined in CUPS (or use the 'default' one)")

add_default_option("PRINTER", "printer_options", {},
                   "Print options passed to the printer, shall be a valid Python dictionary")

add_default_option("PRINTER", "printer_delay", 10,
                   "How long is the print view in seconds (0 to skip it)",
                   "Time to show print screen", [str(i) for i in range(0, 21)])

add_default_option("PRINTER", "auto_print", 0,
                   "Number of pages automatically sent to the printer (or use 'max' to reach max duplicate)",
                   "Automatically printed pages", [str(i) for i in range(0, 11)] + ['max'])

add_default_option("PRINTER", "max_pages", -1,
                   "Maximum number of printed pages before warning on paper/ink levels (-1 = infinite)",
                   "Maximum of printed pages", [str(i) for i in range(-1, 1000)])

add_default_option("PRINTER", "max_duplicates", 3,
                   "Maximum number of duplicate pages sent to the printer (avoid paper waste)",
                   "Maximum of printed duplicates", [str(i) for i in range(0, 10)])

# --- CONTROLS -----------------------------------------------------------------

add_default_option("CONTROLS", "debounce_delay", 0.3,
                   "How long to press a single hardware button in seconds")

add_default_option("CONTROLS", "multi_press_delay", 0.5,
                   "How long to press multiple hardware buttons in seconds")

add_default_option("CONTROLS", "capture_btn_pin", 11,
                   "Physical GPIO IN pin to take a capture sequence")

add_default_option("CONTROLS", "capture_led_pin", 7,
                   "Physical GPIO OUT pin to light a LED when capture button is pressed")

add_default_option("CONTROLS", "print_btn_pin", 13,
                   "Physical GPIO IN pin to print a picture")

add_default_option("CONTROLS", "print_led_pin", 15,
                   "Physical GPIO OUT pin to light a LED when print button is pressed")
