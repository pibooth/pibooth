# -*- coding: utf-8 -*-

"""Script to display the configuration of the printer.
"""

import sys
import json
import argparse
from pibooth.utils import LOGGER, configure_logging
from pibooth.config import PiboothConfigParser
from pibooth.plugins import create_plugin_manager


def main():
    """Application entry point.
    """
    parser = argparse.ArgumentParser(usage="%(prog)s [options]",
                                     description="Display the options of the printer defined in the "
                                                 "pibooth configuration with their possible values.")
    parser.add_argument("config_directory", nargs='?', default="~/.config/pibooth",
                        help="path to configuration directory (default: %(default)s)")
    parser.add_argument('--json', action='store_true',
                        help="print the current options as a JSON dictionary")
    options = parser.parse_args()

    configure_logging()

    try:
        import cups
    except Exception as ex:
        LOGGER.error("The 'pycups' package is required (pip install pibooth[printer]): %s", ex)
        sys.exit(1)

    plugin_manager = create_plugin_manager()
    config = PiboothConfigParser(f"{options.config_directory}/pibooth.cfg", plugin_manager)

    conn = cups.Connection()
    name = config.get('PRINTER', 'printer_name')
    printers = conn.getPrinters()

    if not name or name.lower() == 'default':
        if not printers:
            LOGGER.warning("No printer configured in CUPS (see http://localhost:631)")
            return
        name = conn.getDefault() or list(printers.keys())[0]  # Take first one
    elif name not in printers:
        LOGGER.warning("No printer named '%s' in CUPS (see http://localhost:631)", name)
        return

    LOGGER.info("Connected to printer '%s'", name)

    ppd = cups.PPD(conn.getPPD(name))
    groups = ppd.optionGroups
    printer_options = []
    for group in groups:
        group_name = f"{group.name} - {group.text}"
        for opt in group.options:
            option = {'group': group_name}
            values = [choice["choice"] for choice in opt.choices]
            texts = [choice["text"] for choice in opt.choices]
            option['keyword'] = opt.keyword
            option['value'] = opt.defchoice
            option['description'] = opt.text
            if values != texts:
                option['choices'] = dict([(v, texts[values.index(v)]) for v in values])
            else:
                option['choices'] = values
            printer_options.append(option)

    if options.json:
        print(json.dumps(dict([(option['keyword'], option['value']) for option in printer_options])))
    else:
        for option in printer_options:
            print(f"{option['keyword']} = {option['value']}")
            print(f"     Description: {option['description']}")
            if isinstance(option['choices'], dict):
                choices = [f"{value} = {descr}" for value, descr in option['choices'].items()]
                print(f"     Choices:     {choices[0]}")
                for choice in choices[1:]:
                    print(f"                  {choice}")
            else:
                print("     Choices:     {}".format(", ".join(option['choices'])))

            print()


if __name__ == "__main__":
    main()
