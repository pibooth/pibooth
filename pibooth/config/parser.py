# -*- coding: utf-8 -*-

"""Pibooth configuration.
"""

import io
import ast
import os
import os.path as osp
import itertools
import inspect
from collections import OrderedDict as odict
from pibooth.utils import LOGGER, open_text_editor
from pibooth import language
from pibooth.plugins import get_plugin_name


try:
    from configparser import ConfigParser
except ImportError:
    # Python 2.x fallback
    from ConfigParser import ConfigParser

try:
    basestring
except NameError:
    # Python 3.x fallback
    basestring = str


def values_list_repr(values):
    """Concatenate a list of values to a readable string.
    """
    return "'{}' or '{}'".format("', '".join([str(i) for i in values[:-1]]), values[-1])


DEFAULT = odict((
    ("GENERAL",
        odict((
            ("language",
                ("en",
                 "User interface language: {}".format(values_list_repr(language.get_supported_languages())),
                 "UI language", language.get_supported_languages())),
            ("directory",
                ("~/Pictures/pibooth",
                 "Path to save pictures (list of quoted paths accepted)",
                 None, None)),
            ("autostart",
                (False,
                 "Start pibooth at Raspberry Pi startup",
                 "Auto-start", ['True', 'False'])),
            ("debug",
                (False,
                 "In debug mode, exceptions are not caught, logs are more verbose, pictures are cleared at startup",
                 "Debug mode", ['True', 'False'])),
            ("plugins",
                ('',
                 "Path to custom plugin(s) not installed with pip (list of quoted paths accepted)",
                 None, None)),
        ))
     ),
    ("WINDOW",
        odict((
            ("size",
                ((800, 480),
                 "The (width, height) of the display window or 'fullscreen'",
                 'Startup size', ['(800, 480)', 'fullscreen'])),
            ("background",
                ((0, 0, 0),
                 "Background RGB color or image path",
                 None, None)),
            ("text_color",
                ((255, 255, 255),
                 "Text RGB color",
                 "Text RGB color", (255, 255, 255))),
            ("flash",
                (True,
                 "Blinking background when a capture is taken",
                 "Flash on capture", ['True', 'False'])),
            ("animate",
                (False,
                 "Animate the last taken picture by displaying captures one by one",
                 "Animated picture", ['True', 'False'])),
            ("animate_delay",
                (0.2,
                 "How long is displayed the capture in seconds before switching to the next one",
                 None, None)),
            ("final_image_delay",
                (-1,
                 "How long is displayed the final picture in seconds before being hidden (-1 if never hidden)",
                 "Final image display time", ['-1'] + [str(i) for i in range(0, 121, 5)])),
            ("arrows",
                ('bottom',
                 "Show arrows to indicate physical buttons: 'bottom', 'top' or 'hidden'",
                 "Show button arrows", ['bottom', 'top', 'hidden'])),
            ("arrows_x_offset",
                (0,
                 "Apply horizontal offset to arrows position",
                 None, None)),
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
                 "Stop the preview before taking the capture",
                 None, None)),
        ))
     ),
    ("PICTURE",
        odict((
            ("orientation",
                ("auto",
                 "Orientation of the final picture: 'auto', 'portrait' or 'landscape'",
                 "Orientation", ['auto', 'portrait', 'landscape'])),
            ("captures",
                ((4, 1),
                 "Possible choice(s) of captures numbers (numbers between 1 to 4)",
                 "Number of captures", ['1', '2', '3', '4'] + [str(val) for val in itertools.permutations(range(1, 5), 2)])),
            ("captures_effects",
                ("none",
                 "Effect applied to the captures (list of quoted names accepted)",
                 None, None)),
            ("captures_cropping",
                (False,
                 "Crop each capture border in order to fit the paper size",
                 "Crop captures",  ['True', 'False'])),
            ("margin_thick",
                (100,
                 "Thick (in pixels) between captures and picture borders/texts",
                 "Borders width", [str(i) for i in range(0, 210, 10)])),
            ("footer_text1",
                ("Footer 1",
                 "Main text displayed",
                 "Title", "")),
            ("footer_text2",
                ("Footer 2",
                 "Secondary text displayed",
                 "Sub-title", "")),
            ("text_colors",
                ((0, 0, 0),
                 "RGB colors used for footer texts (list of tuples accepted)",
                 None, None)),
            ("text_fonts",
                (('Amatic-Bold', 'AmaticSC-Regular'),
                 "Fonts name or file path used for footer texts (list of quoted names accepted)",
                 None, None)),
            ("text_alignments",
                ('center',
                 "Alignments used for footer texts: 'left', 'center' or 'right' (list of quoted names accepted)",
                 None, None)),
            ("overlays",
                ('',
                 "Overlay path (PNG file) with same aspect ratio than final picture (list of quoted paths accepted)",
                 None, None)),
            ("backgrounds",
                ((255, 255, 255),
                 "Background RGB color or image path (list of tuples or quoted paths accepted)",
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
                 "Flip horizontally the capture",
                 None, None)),
            ("rotation",
                (0,
                 "Rotation of the camera: 0, 90, 180 or 270",
                 None, None)),
            ("resolution",
                ((1934, 2464),
                 "Resolution for camera captures (preview will have same aspect ratio)",
                 None, None)),
            ("delete_internal_memory",
                (False,
                 "Delete captures from camera internal memory (when applicable)",
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
            ("max_pages",
                (-1,
                 "Maximum number of printed pages before warning on paper/ink levels (-1 = infinite)",
                 'Maximum of printed pages', [str(i) for i in range(-1, 1000)])),
            ("max_duplicates",
                (3,
                 "Maximum number of duplicate pages sent to the printer (avoid paper waste)",
                 'Maximum of printed duplicates', [str(i) for i in range(0, 10)])),
            ("pictures_per_page",
                (1,
                 "Print 1, 2, 3 or 4 picture copies per page",
                 'Number of copies per page', [str(i) for i in range(1, 5)])),
        ))
     ),
    ("CONTROLS",
        odict((
            ("debounce_delay",
                (0.3,
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
        ))
     ),
))


class PiConfigParser(ConfigParser):

    """Enhenced configuration file parser.
    """

    def __init__(self, filename, plugin_manager):
        ConfigParser.__init__(self)
        self._pm = plugin_manager
        self.filename = osp.abspath(osp.expanduser(filename))

        if osp.isfile(self.filename):
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

        with io.open(self.filename, 'w', encoding="utf-8") as fp:
            for section, options in DEFAULT.items():
                fp.write("[{}]\n".format(section))
                for name, value in options.items():
                    if default:
                        val = value[0]
                    else:
                        val = self.get(section, name)
                    fp.write("# {}\n{} = {}\n\n".format(value[1], name, val))

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
        filename = osp.expanduser('~/.config/autostart/pibooth.desktop')
        dirname = osp.dirname(filename)
        enable = self.getboolean('GENERAL', 'autostart')
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
            plugin_name = get_plugin_name(self._pm, plugin, False)

        # Check that the option is not already created
        if section in DEFAULT and option in DEFAULT[section]:
            raise ValueError("The plugin '{}' try to define the option [{}][{}] "
                             "which is already defined.".format(plugin_name, section, option))

        # Add the option to the default dictionary
        description = "{}\n# Required by '{}' plugin".format(description, plugin_name)
        DEFAULT.setdefault(section, odict())[option] = (default, description, menu_name, menu_choices)

    def get(self, section, option, **kwargs):
        """Override the default function of ConfigParser to add a
        default value if section or option is not found.

        :param section: config section name
        :type section: str
        :param option: option name
        :type option: str
        """
        if self.has_section(section) and self.has_option(section, option):
            return ConfigParser.get(self, section, option, **kwargs)
        return str(DEFAULT[section][option][0])

    def set(self, section, option, value=None):
        """Override the default function of ConfigParser to create
        the section if it does not exist."""
        if not self.has_section(section):
            self.add_section(section)
        super(PiConfigParser, self).set(section, option, value)

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

        if str in types:  # Python 2.x compat
            types[types.index(str)] = basestring

        color = False
        if 'color' in types:
            types.remove('color')
            types.append(tuple)
            types.append(list)
            color = True  # Option accept color tuples

        path = False
        if 'path' in types:
            types.remove('path')
            types.append(basestring)
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
                if isinstance(v, basestring):
                    new_values.append(self._get_abs_path(v))
                else:
                    new_values.append(v)
            values = tuple(new_values)

        while len(values) < extend:
            values += (values[-1],)
        return values
