# -*- coding: utf-8 -*-

"""Pibooth configuration.
"""

import io
import ast
import os
import os.path as osp

import inspect
from configparser import RawConfigParser
from pibooth.config.default import DEFAULT, add_default_option
from pibooth.utils import LOGGER, open_text_editor


class PiboothConfigParser(RawConfigParser):

    """Class to parse and store the configuration values.

    The following attributes are available for use in plugins (``cfg`` reprensents
    the PiboothConfigParser instance):

        - ``cfg.filename`` (str): absolute path to the laoded config file
        - ``cfg.autostart_filename`` (str): file used to start pibooth at Raspberry Pi startup
    """

    def __init__(self, filename, plugin_manager, load=True):
        super().__init__()
        self._pm = plugin_manager

        # ---------------------------------------------------------------------
        # Variables shared with plugins
        # Change them may break plugins compatibility
        self.filename = osp.abspath(osp.expanduser(filename))
        self.autostart_filename = osp.expanduser('~/.config/autostart/pibooth.desktop')
        # ---------------------------------------------------------------------

        if osp.isfile(self.filename) and load:
            self.load()

    def _get_abs_path(self, path):
        """Return absolute path. In case of relative path given, the absolute
        one is created using config file path as reference path.
        """
        if not path:  # Empty string, don't process it as it is not a path
            return path
        path = osp.expanduser(path)
        if not osp.isabs(path):
            path = osp.join(osp.relpath(osp.dirname(self.filename), '.'), path)
        return osp.abspath(path)

    def save(self, default=False):
        """Save the current or default values into the configuration file.
        """
        LOGGER.info("Generate the configuration file in '%s'", self.filename)

        dirname = osp.dirname(self.filename)
        if not osp.isdir(dirname):
            os.makedirs(dirname)

        option_pattern = "# {comment}\n{name} = {value}\n\n"

        with io.open(self.filename, 'w', encoding="utf-8") as fp:
            for section, options in DEFAULT.items():
                # 1. Write defined options
                fp.write(f"[{section}]\n")
                for name, value in options.items():
                    if default:
                        val = value[0]
                    else:
                        val = self.get(section, name)
                    fp.write(option_pattern.format(comment=value[1], name=name, value=val))

                if not default and self.has_section(section):
                    # 2. Write options that are not in DEFAULT (maybe an option from a disabled plugin)
                    for name, value in self.items(section):
                        if name not in DEFAULT[section]:
                            fp.write(option_pattern.format(comment="Unknown option, maybe from a disabled plugin?",
                                                           name=name, value=value))

            if not default:
                # 3. Write sections that are not in DEFAULT (maybe a section from a disabled plugin)
                for section in self.sections():
                    if section not in DEFAULT:
                        fp.write(f"[{section}]\n")
                        for name, value in self.items(section):
                            fp.write(option_pattern.format(comment="Unknown option, maybe from a disabled plugin?",
                                                           name=name, value=value))

        self.handle_autostart()

    def load(self):
        """Load configuration from file.
        """
        self.read(self.filename, encoding="utf-8")
        self.handle_autostart()

    def edit(self):
        """Open a text editor to edit the configuration.
        """
        if open_text_editor(self.filename):
            # Reload config to check if autostart has changed
            self.load()

    def handle_autostart(self):
        """Handle desktop file to start pibooth at the Raspberry Pi startup.
        """
        dirname = osp.dirname(self.autostart_filename)
        enable = self.getboolean('GENERAL', 'autostart')
        delay = self.getint('GENERAL', 'autostart_delay')
        if enable:
            regenerate = True
            if osp.isfile(self.autostart_filename):
                with open(self.autostart_filename, 'r') as fp:
                    txt = fp.read()
                    if delay > 0 and f"sleep {delay}" in txt or delay <= 0 and "sleep" not in txt:
                        regenerate = False

            if regenerate:
                if not osp.isdir(dirname):
                    os.makedirs(dirname)

                LOGGER.info("Generate the auto-startup file in '%s'", dirname)
                with open(self.autostart_filename, 'w') as fp:
                    fp.write("[Desktop Entry]\n")
                    fp.write("Name=pibooth\n")
                    if delay > 0:
                        fp.write(f"Exec=bash -c \"sleep {delay} && pibooth\"\n")
                    else:
                        fp.write("Exec=pibooth\n")
                    fp.write("Type=application\n")

        elif not enable and osp.isfile(self.autostart_filename):
            LOGGER.info("Remove the auto-startup file in '%s'", dirname)
            os.remove(self.autostart_filename)

    def join_path(self, *names):
        """Return the directory path of the configuration file
        and join it the given names.

        :param names: names to join to the directory path
        :type names: str
        """
        return osp.join(osp.dirname(self.filename), *names)

    def add_option(self, section, option, default, description, menu_name=None, menu_choices=None):
        """Add a new option to the configuration and defines its default value.

        :param section: section in which the option is declared
        :type section: str
        :param option: option name
        :type option: str
        :param default: default value of the option
        :type default: any
        :param description: description to put in the configuration
        :type description: str
        :param menu_name: option label on graphical menu (hidden if None)
        :type menu_name: str
        :param menu_choices: option possible choices on graphical menu
        :type menu_choices: any
        """
        assert section, "Section name can not be empty string"
        assert option, "Option name can not be empty string"
        assert description, "Description can not be empty string"

        # Find the caller plugin
        stack = inspect.stack()
        if len(stack) < 2:
            plugin_name = "Unknown"
        else:
            plugin = inspect.getmodule(inspect.stack()[1][0])
            plugin_name = self._pm.get_friendly_name(plugin, False)

        # Check that the option is not already created
        if section in DEFAULT and option in DEFAULT[section]:
            raise ValueError("The plugin '{}' try to define the option [{}][{}] "
                             "which is already defined.".format(plugin_name, section, option))

        # Add the option to the default dictionary
        description = "{}\n# Required by '{}' plugin".format(description, plugin_name)
        add_default_option(section, option, default, description, menu_name, menu_choices)

    def get(self, section, option, **kwargs):
        """Get a value from config. Return the default value if the section
        or option is not defined.

        :param section: config section name
        :type section: str
        :param option: option name
        :type option: str

        :return: value
        :rtype: str
        """
        if self.has_section(section) and self.has_option(section, option):
            return super().get(section, option, **kwargs)
        return str(DEFAULT[section][option][0])

    def set(self, section, option, value=None):
        """Set a value to config. Create the section if it is not defined.

        :param section: config section name
        :type section: str
        :param option: option name
        :type option: str
        :param value: value to set
        :type value: str
        """
        if not self.has_section(section):
            self.add_section(section)
        super().set(section, option, value)

    def gettyped(self, section, option):
        """Get a value from config and try to convert it in a native Python
        type (using the :py:mod:`ast` module).

        :param section: config section name
        :type section: str
        :param option: option name
        :type option: str
        """
        value = self.get(section, option)
        try:
            return ast.literal_eval(value)
        except (ValueError, SyntaxError):
            return value

    def getpath(self, section, option):
        """Get a path from config, evaluate the absolute path from configuration
        file path.

        :param section: config section name
        :type section: str
        :param option: option name
        :type option: str
        """
        return self._get_abs_path(self.get(section, option))

    @staticmethod
    def _get_authorized_types(types):
        """Get a tuple of authorized types and if the color and path are accepted
        """
        if not isinstance(types, (tuple, list)):
            types = [types]
        else:
            types = list(types)

        color = False
        if 'color' in types:
            types.remove('color')
            types.append(tuple)
            types.append(list)
            color = True  # Option accept color tuples

        path = False
        if 'path' in types:
            types.remove('path')
            types.append(str)
            path = True  # Option accept file path

        types = tuple(types)

        return types, color, path

    def gettuple(self, section, option, types, extend=0):
        """Get a list of values from config. The values type shall be in the
        list of authorized types. This method permits to get severals values
        from the same configuration option.

        If the option contains one value (with acceptable type), a tuple
        with one element is created and returned.

        :param section: config section name
        :type section: str
        :param option: option name
        :type option: str
        :param types: list of authorized types
        :type types: list
        :param extend: extend the tuple with the last value until length is reached
        :type extend: int
        """
        values = self.gettyped(section, option)
        types, color, path = self._get_authorized_types(types)

        if not isinstance(values, (tuple, list)):
            if not isinstance(values, types):
                raise ValueError("Invalid config value [{}][{}]={}".format(section, option, values))
            if values == '' and extend == 0:
                # Empty config key and empty tuple accepted
                values = ()
            else:
                values = (values,)
        else:
            # Check if one value is given or if it is a list of value
            if color and len(values) == 3 and all(isinstance(elem, int) for elem in values):
                values = (values,)
            elif not all(isinstance(elem, types) for elem in values):
                raise ValueError("Invalid config value [{}][{}]={}".format(section, option, values))

        if path:
            new_values = []
            for v in values:
                if isinstance(v, str):
                    new_values.append(self._get_abs_path(v))
                else:
                    new_values.append(v)
            values = tuple(new_values)

        while len(values) < extend:
            values += (values[-1],)
        return values
