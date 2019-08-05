# -*- coding: utf-8 -*-

"""Pibooth configuration.
"""

import ast
import os
import os.path as osp
import errno
import subprocess
import itertools
from collections import OrderedDict as odict
import pibooth
from pibooth.utils import LOGGER

try:
    from configparser import ConfigParser
except ImportError:
    # Python 2.x fallback
    from ConfigParser import ConfigParser


def get_supported_languages():
    """Return the list of supported language.
    """
    path = osp.join(osp.dirname(osp.abspath(pibooth.__file__)), 'pictures')
    return [name for name in os.listdir(path) if osp.isdir(osp.join(path, name))
            and not name.startswith('.') and not name.startswith('__') and name != 'com']


def values_list_repr(values):
    """Concatenate a list of values to a readable string.
    """
    return "'{}' or '{}'".format("', '".join([str(i) for i in values[:-1]]), values[-1])


DEFAULT = odict((
    ("GENERAL",
        odict((
            ("language",
                ("en",
                 "User interface language ({})".format(values_list_repr(get_supported_languages())),
                 "UI language", get_supported_languages())),
            ("directory",
                ("~/Pictures/pibooth",
                 "Path to save pictures",
                 None, None)),
            ("clear_on_startup",
                (True,
                 "Cleanup the 'directory' before start",
                 "Clear on startup", ['True', 'False'])),
            ("autostart",
                (False,
                 "Start pibooth at Raspberry Pi startup",
                 "Auto-start", ['True', 'False'])),
            ("failsafe",
                (True,
                 "Show fail message and go back to wait state in case of exception",
                 "Fail safe", ['True', 'False'])),
        ))
     ),
    ("WINDOW",
        odict((
            ("size",
                ((800, 480),
                 "The (width, height) of the display window or 'fullscreen'",
                 'Startup size', ['(800, 480)', 'fullscreen'])),
            ("flash",
                (True,
                 "Blinking background when picture is taken",
                 "Flash on capture", ['True', 'False'])),
            ("arrows",
                ('bottom',
                 "Show arrows to indicate physical buttons ('bottom', 'top' or 'hidden')",
                 "Show button arrows", ['bottom', 'top', 'hidden'])),
            ("arrows_x_offset",
                (0,
                 "Apply horizontal offset to arrows position",
                 "Arrows horizontal offset", [str(i) for i in range(-300, 300, 10)])),
            ("preview_delay",
                (3,
                 "How long is the preview in seconds",
                 "Preview delay", [str(i) for i in range(1, 21)])),
            ("preview_countdown",
                (True,
                 "Show a countdown timer during the preview",
                 "Preview countdown", ['True', 'False'])),
            ("preview_stop_on_capture",
                (False,
                 "Stop the preview before taking the picture",
                 None, None)),
        ))
     ),
    ("PICTURE",
        odict((
            ("captures",
                ((4, 1),
                 "Possible choice(s) of captures numbers (numbers between 1 to 4 max)",
                 "Number of captures", ['1', '2', '3', '4'] + [str(val) for val in itertools.permutations(range(1, 5), 2)])),
            ("orientation",
                ("auto",
                 "Orientation of the final image ('auto', 'portrait' or 'landscape')",
                 "Orientation", ['auto', 'portrait', 'landscape'])),
            ("effect",
                ("none",
                 "Effect applied to the captures (a list of quoted names can be given)",
                 None, None)),
            ("footer_text1",
                ("Footer 1",
                 "Main text displayed",
                 "Title : ", "")),
            ("footer_text2",
                ("Footer 2",
                 "Secondary text displayed",
                 "Sub-title : ", "")),
            ("text_color",
                ((0, 0, 0),
                 "Footer text RGB color",
                 None, None)),
            ("bg_color",
                ((255, 255, 255),
                 "Background RGB color or path to a background image",
                 None, None)),
            ("fonts",
                (('Amatic-Bold', 'AmaticSC-Regular'),
                 "Font name/path/url to be used for footer texts (1 or 2 names/paths)",
                 None, None)),
        ))
     ),
    ("CAMERA",
        odict((
            ("iso",
                (100,
                 "Adjust for lighting issues, normal is 100 or 200 and dark is 800 max",
                 None, None)),
            ("flip",
                (False,
                 "Flip horizontally the captured picture",
                 None, None)),
            ("rotation",
                (0,
                 "Rotation of the camera (0, 90, 180 or 270)",
                 None, None)),
            ("resolution",
                ((1934, 2464),
                 "Resolution for camera captures (preview will have same aspect ratio)",
                 None, None)),
        ))
     ),
    ("PRINTER",
        odict((
            ("printer_name",
                ("default",
                 "Name of the printer defined in CUPS (or use the 'default' one)",
                 None, None)),
            ("printer_delay",
                (10,
                 "How long is the print view in seconds (0 to skip it)",
                 "Time to show print screen", [str(i) for i in range(0, 21)])),
            ("max_duplicates",
                (3,
                 "Maximum number of duplicate pages sent to the printer (avoid paper wast)",
                 'Maximum of printed duplicates', [str(i) for i in range(1, 5)])),
            ("nbr_copies",
                (1,
                 "Prints 1, 2, 3 or 4 picture copies per page",
                 'Number of copies per page', [str(i) for i in range(1, 5)])),
        ))
     ),
    ("CONTROLS",
        odict((
            ("debounce_delay",
                (0.5,
                 "How long to debounce the hardware buttons in seconds",
                 None, None)),
            ("picture_btn_pin",
                (11,
                 "Physical GPIO IN pin to take a picture",
                 None, None)),
            ("picture_led_pin",
                (7,
                 "Physical GPIO OUT pin to light a LED when picture button is pressed",
                 None, None)),
            ("print_btn_pin",
                (13,
                 "Physical GPIO IN pin to print a picture",
                 None, None)),
            ("print_led_pin",
                (15,
                 "Physical GPIO OUT pin to light a LED when print button is pressed",
                 None, None)),
            ("startup_led_pin",
                (29,
                 "Physical GPIO OUT pin to light a LED at pibooth startup",
                 None, None)),
            ("preview_led_pin",
                (31,
                 "Physical GPIO OUT pin to light a LED during preview",
                 None, None)),
        ))
     ),
))


class PiConfigParser(ConfigParser):

    """Enhenced configuration file parser.
    """

    language = 'en'
    editors = ['leafpad', 'vi', 'emacs']

    def __init__(self, filename, clear=False):
        ConfigParser.__init__(self)
        self.filename = osp.abspath(osp.expanduser(filename))

        if not osp.isfile(self.filename) or clear:
            dirname = osp.dirname(self.filename)
            if not osp.isdir(dirname):
                os.makedirs(dirname)
            self.save(True)
            self.enable_autostart(DEFAULT['GENERAL']['autostart'][0])

        self.read(self.filename)

    def save(self, default=False):
        """Save the current or default values into the configuration file.
        """
        LOGGER.info("Generate the configuration file in '%s'", self.filename)
        with open(self.filename, 'w') as fp:
            for section, options in DEFAULT.items():
                fp.write("[{}]\n".format(section))
                for name, value in options.items():
                    if default:
                        val = value[0]
                    else:
                        val = self.get(section, name)
                    fp.write("# {}\n{} = {}\n\n".format(value[1], name, val))

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

    def open_editor(self):
        """Open a text editor to edit the configuration file.
        """
        for editor in self.editors:
            try:
                process = subprocess.Popen([editor, self.filename])
                process.communicate()
                self.read(self.filename)
                return
            except OSError as e:
                if e.errno != errno.ENOENT:
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
