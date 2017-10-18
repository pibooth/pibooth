#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Photo booth main module.
"""

import ast
import os.path as osp
from ConfigParser import ConfigParser


class PtbConfigParser(ConfigParser):

    """Enhenced configuration file parser.
    """

    def __init__(self, filename):
        ConfigParser.__init__(self)
        if not osp.isfile(filename):
            raise ValueError("No sush configuration file: '%s'" % filename)
        self.filename = filename
        self.read(filename)

    def get(self, section, option, default=None):
        """
        Override the default function of ConfigParser to add a
        default value if section or option is not found.

        :param default: default value if section or option is not found
        :type default: str
        """
        if self.has_section(section) and self.has_option(section, option):
            value = ConfigParser.get(self, section, option)
            return value
        return default

    def gettyped(self, section, option, default=None):
        """
        Get a value from config and try to convert it in a native Python
        type (using the :py:mod:`ast` module).

        :param default: default value if section or option is not found
        :type default: str
        """
        value = self.get(section, option, default)
        try:
            return ast.literal_eval(value)
        except (ValueError, SyntaxError):
            return value


def main():
    config = PtbConfigParser(osp.join(osp.dirname(osp.abspath(__file__)), "config.ini"))


if __name__ == '__main__':
    main()
