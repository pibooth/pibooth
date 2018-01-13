#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Photobooth configuration.
"""

import ast
import os
import os.path as osp
import subprocess
try:
    import configparser
except ImportError:
    # Python 2.x fallback
    import ConfigParser as configparser


DEFAULT = {
    "GENERAL": {
        "directory": ("~/Pictures/pibooth", "Path to save images"),
        "clear_on_startup": (True, "Clear previously stored photos"),
        "debounce_delay": (0.3, "How long to debounce the button in seconds"),
    },
    "PICTURE": {
        "captures": (4, "How many pictures to take (4 max)"),
        "footer_text1": ("Footer 1", "First text displayed"),
        "footer_text2": ("Footer 2", "Second text displayed"),
        "bg_color": ((255, 255, 255), "Background RGB color"),
        "text_color": ((0, 0, 0), "Footer text RGB color"),
    },
    "WINDOW": {
        "size": ((800, 480), "(Width, Height) of the display monitor"),
        "flash": (True, "Blinking background when picture is taken"),
        "preview_countdown": (True, "Show a countdown timer during the preview"),
        "preview_delay": (3, "How long is the preview in seconds"),
    },
    "CAMERA": {
        "iso": (100, "Adjust for lighting issues. Normal is 100 or 200. Dark is 800 max"),
        "resolution": ((1920, 1080), "Resolution for camera captures (see picamera modes)"),
    }
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


class PtbConfigParser(configparser.ConfigParser):

    """Enhenced configuration file parser.
    """

    def __init__(self, filename, clear=False):
        configparser.ConfigParser.__init__(self)
        self.filename = osp.abspath(osp.expanduser(filename))

        if not osp.isfile(self.filename) or clear:
            print("Generate the configuration file in '{}'".format(self.filename))
            dirname = osp.dirname(self.filename)
            if not osp.isdir(dirname):
                os.makedirs(dirname)
            generate_default_config(self.filename)

        self.read(self.filename)

    def get(self, section, option, **kwargs):
        """
        Override the default function of ConfigParser to add a
        default value if section or option is not found.
        """
        if self.has_section(section) and self.has_option(section, option):
            return configparser.ConfigParser.get(self, section, option, **kwargs)
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
