#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Photobooth configuration.
"""

import ast
import os
import os.path as osp
import subprocess
from pibooth.utils import LOGGER

try:
    from configparser import ConfigParser
except ImportError:
    # Python 2.x fallback
    from ConfigParser import ConfigParser


DEFAULT = {
    "GENERAL": {
        "directory": ("~/Pictures/pibooth", "Path to save pictures"),
        "clear_on_startup": (True, "Cleanup the 'directory' before start"),
        "debounce_delay": (0.3, "How long to debounce the button in seconds"),
        "language": ("en", "User interface language (fallback to English if not found)"),
    },
    "PICTURE": {
        "captures": (4, "Number pictures in case of multiple captures (4 max)"),
        "orientation": ("portrait", "Orientation of the final image (portrait or landscape")
        "footer_text1": ("Footer 1", "First text displayed"),
        "footer_text2": ("Footer 2", "Second text displayed"),
        "bg_color": ((255, 255, 255), "Background RGB color"),
        "text_color": ((0, 0, 0), "Footer text RGB color"),
    },
    "WINDOW": {
        "size": ((800, 480), "(Width, Height) of the display monitor or 'fullscreen'"),
        "flash": (True, "Blinking background when picture is taken"),
        "preview_delay": (3, "How long is the preview in seconds"),
        "preview_countdown": (True, "Show a countdown timer during the preview"),
    },
    "CAMERA": {
        "iso": (100, "Adjust for lighting issues. Normal is 100 or 200. Dark is 800 max"),
        "flip": (False, "Flip horizontally the captured picture"),
        "rotation": (0, "Rotation of the camera (valid values are 0, 90, 180, and 270)"),
        "resolution": ((1934, 2464), "Resolution for camera captures (preview will have same aspect ratio)"),
    },
    "PRINTER": {
        "printer_name": ("default", "Name of the printer to send the pictures"),
        "printer_delay": (10, "How long is the print view in seconds (0 to skip it)"),
    },
}


def generate_default_config(filename):
    """Genrate the default configuration.
    """
    with open(filename, 'w') as fp:
        for section, options in DEFAULT.items():
            fp.write("[{}]\n".format(section))
            for name, value in options.items():
                fp.write("# {}\n{} = {}\n\n".format(value[1], name, value[0]))


def edit_configuration(config):
    """Open a text editor to edit the configuration file.
    """
    process = subprocess.Popen(['leafpad', config.filename])
    process.communicate()


class PtbConfigParser(ConfigParser):

    """Enhenced configuration file parser.
    """

    language = None

    def __init__(self, filename, clear=False):
        ConfigParser.__init__(self)
        self.filename = osp.abspath(osp.expanduser(filename))

        if not osp.isfile(self.filename) or clear:
            LOGGER.info("Generate the configuration file in '%s'", self.filename)
            dirname = osp.dirname(self.filename)
            if not osp.isdir(dirname):
                os.makedirs(dirname)
            generate_default_config(self.filename)

        self.read(self.filename)

        # Handle the language configuration, save it as a class attribute for easy access
        path = osp.join(osp.dirname(osp.abspath(__file__)), 'pictures')
        possibles = [name for name in os.listdir(path) if osp.isdir(osp.join(path, name))]
        language = self.get('GENERAL', 'language')
        if language not in possibles:
            LOGGER.warning("Unsupported language '%s', fallback to English", language)
            PtbConfigParser.language = 'en'
        else:
            PtbConfigParser.language = language

    def get(self, section, option, **kwargs):
        """
        Override the default function of ConfigParser to add a
        default value if section or option is not found.
        """
        if self.has_section(section) and self.has_option(section, option):
            return ConfigParser.get(self, section, option, **kwargs)
        return str(DEFAULT[section][option][0])

    def gettyped(self, section, option):
        """
        Get a value from config and try to convert it in a native Python
        type (using the :py:mod:`ast` module).
        """
        value = self.get(section, option)
        try:
            return ast.literal_eval(value)
        except (ValueError, SyntaxError):
            return value
