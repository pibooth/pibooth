# -*- coding: utf-8 -*-

"""Pibooth configuration.
"""

import ast
import os
import os.path as osp
import subprocess
from collections import OrderedDict as odict
from pibooth.utils import LOGGER

try:
    from configparser import ConfigParser
except ImportError:
    # Python 2.x fallback
    from ConfigParser import ConfigParser


def get_supported_languages():
    """Return the list of supported language.
    """
    path = osp.join(osp.dirname(osp.abspath(__file__)), 'pictures')
    return [name for name in os.listdir(path) if osp.isdir(osp.join(path, name))
            and not name.startswith('.') and not name.startswith('__')]


def values_list_repr(values):
    """Concatenate a list of values to a readable string.
    """
    return "'{}' or '{}'".format("', '".join([str(i) for i in values[:-1]]), values[-1])


DEFAULT = odict((
    ("GENERAL",
        odict((
            ("language", ("en", "User interface language ({})".format(values_list_repr(get_supported_languages())))),
            ("directory", ("~/Pictures/pibooth", "Path to save pictures")),
            ("clear_on_startup", (True, "Cleanup the 'directory' before start")),
            ("autostart", (False, "Start pibooth at Raspberry Pi startup")),
            ("failsafe", (True, "Show fail message and go back to wait state in case of exception")),
        ))
     ),
    ("WINDOW",
        odict((
            ("size", ((800, 480), "The (width, height) of the display window or 'fullscreen'")),
            ("flash", (True, "Blinking background when picture is taken")),
            ("preview_delay", (3, "How long is the preview in seconds")),
            ("preview_countdown", (True, "Show a countdown timer during the preview")),
            ("preview_stop_on_capture", (False, "Stop the preview before taking the picture")),
        ))
     ),
    ("PICTURE",
        odict((
            ("captures", ((4, 1), "Possible choice(s) of captures numbers (numbers between 1 to 4 max)")),
            ("orientation", ("auto", "Orientation of the final image ('auto', 'portrait' or 'landscape')")),
            ("footer_text1", ("Footer 1", "Main text displayed")),
            ("footer_text2", ("Footer 2", "Secondary text displayed")),
            ("text_color", ((0, 0, 0), "Footer text RGB color")),
            ("bg_color", ((255, 255, 255), "Background RGB color or path to a background image")),
        ))
     ),
    ("CAMERA",
        odict((
            ("iso", (100, "Adjust for lighting issues, normal is 100 or 200 and dark is 800 max")),
            ("flip", (False, "Flip horizontally the captured picture")),
            ("rotation", (0, "Rotation of the camera (0, 90, 180 or 270)")),
            ("resolution", ((1934, 2464), "Resolution for camera captures (preview will have same aspect ratio)")),
        ))
     ),
    ("PRINTER",
        odict((
            ("printer_name", ("default", "Name of the printer defined in CUPS (or use the 'default' one)")),
            ("printer_delay", (10, "How long is the print view in seconds (0 to skip it)")),
            ("max_duplicates", (3, "Maximum number of duplicate pages sent to the printer (avoid paper wast)")),
            ("nbr_copies", (1, "Prints 1, 2, 3 or 4 picture copies per page")),
        ))
     ),
    ("CONTROLS",
        odict((
            ("debounce_delay", (0.3, "How long to debounce the hardware buttons in seconds")),
            ("picture_btn_pin", (11, "Physical GPIO IN pin to take a picture")),
            ("picture_led_pin", (7, "Physical GPIO OUT pin to light a LED when picture button is pressed")),
            ("print_btn_pin", (13, "Physical GPIO IN pin to print a picture")),
            ("print_led_pin", (15, "Physical GPIO OUT pin to light a LED when print button is pressed")),
            ("startup_led_pin", (29, "Physical GPIO OUT pin to light a LED at pibooth startup")),
            ("preview_led_pin", (31, "Physical GPIO OUT pin to light a LED during preview")),
        ))
     ),
))


def generate_default_config(filename):
    """Genrate the default configuration.
    """
    with open(filename, 'w') as fp:
        for section, options in DEFAULT.items():
            fp.write("[{}]\n".format(section))
            for name, value in options.items():
                fp.write("# {}\n{} = {}\n\n".format(value[1], name, value[0]))


class PiConfigParser(ConfigParser):

    """Enhenced configuration file parser.
    """

    language = 'en'
    editors = ['leafpad', 'vi', 'emacs']

    def __init__(self, filename, clear=False):
        ConfigParser.__init__(self)
        self.filename = osp.abspath(osp.expanduser(filename))

        if not osp.isfile(self.filename) or clear:
            LOGGER.info("Generate the configuration file in '%s'", self.filename)
            dirname = osp.dirname(self.filename)
            if not osp.isdir(dirname):
                os.makedirs(dirname)
            generate_default_config(self.filename)

        self.reload()

    def reload(self):
        """Reload current configuration file.
        """
        self.read(self.filename)

        # Handle the language configuration, save it as a class attribute for easy access
        language = self.get('GENERAL', 'language')
        if language not in get_supported_languages():
            LOGGER.warning("Unsupported language '%s', fallback to English", language)
        else:
            PiConfigParser.language = language

        # Handle autostart of the application
        self.enable_autostart(self.getboolean('GENERAL', 'autostart'))

    def enable_autostart(self, enable=True):
        """Auto-start pibooth at the Raspberry Pi startup.
        """
        filename = osp.expanduser('~/.config/autostart/pibooth.desktop')
        dirname = osp.dirname(filename)
        if enable and not osp.isfile(filename):

            if not osp.isdir(dirname):
                os.makedirs(dirname)

            LOGGER.info("Generate the auto-startup file in '%s'", dirname)
            with open(filename, 'w') as fp:
                fp.write("[Desktop Entry]\n")
                fp.write("Name=pibooth\n")
                fp.write("Exec=pibooth\n")
                fp.write("Type=application\n")

        elif not enable and osp.isfile(filename):
            LOGGER.info("Remove the auto-startup file in '%s'", dirname)
            os.remove(filename)

    def editor(self):
        """Open a text editor to edit the configuration file.
        """
        for editor in self.editors:
            try:
                process = subprocess.Popen([editor, self.filename])
                process.communicate()
                self.reload()
                return
            except OSError as e:
                if e.errno != os.errno.ENOENT:
                    # Something else went wrong while trying to run the editor
                    raise
        LOGGER.critical("Can't find installed text editor among %s", self.editors)

    def get(self, section, option, **kwargs):
        """Override the default function of ConfigParser to add a
        default value if section or option is not found.
        """
        if self.has_section(section) and self.has_option(section, option):
            return ConfigParser.get(self, section, option, **kwargs)
        return str(DEFAULT[section][option][0])

    def gettyped(self, section, option):
        """Get a value from config and try to convert it in a native Python
        type (using the :py:mod:`ast` module).
        """
        value = self.get(section, option)
        try:
            return ast.literal_eval(value)
        except (ValueError, SyntaxError):
            return value

    def getpath(self, section, option):
        """Get a path from config, evaluate the absolute path from configuration
        file path.
        """
        path = self.get(section, option)
        path = osp.expanduser(path)
        if not osp.isabs(path):
            path = osp.join(osp.relpath(osp.dirname(self.filename), '.'), path)
        return path
