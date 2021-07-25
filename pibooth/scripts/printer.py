# -*- coding: utf-8 -*-

"""Script to display the configuration of the printer.
"""

import cups
from pibooth.utils import LOGGER, configure_logging
from pibooth.config import PiConfigParser
from pibooth.plugins import create_plugin_manager


def main():
    """Application entry point.
    """
    configure_logging()
    plugin_manager = create_plugin_manager()
    config = PiConfigParser("~/.config/pibooth/pibooth.cfg", plugin_manager)

    conn = cups.Connection()
    name = config.get('PRINTER', 'printer_name')

    if not name or name.lower() == 'default':
        name = conn.getDefault()
        if not name and conn.getPrinters():
            name = list(conn.getPrinters().keys())[0]  # Take first one
    elif name not in conn.getPrinters():
        name = None

    if not name:
        if name.lower() == 'default':
            LOGGER.warning("No printer configured in CUPS (see http://localhost:631)")
            return
        else:
            LOGGER.warning("No printer named '%s' in CUPS (see http://localhost:631)", name)
            return
    else:
        LOGGER.info("Connected to printer '%s'", name)

    f = conn.getPPD(name)
    ppd = cups.PPD(f)
    groups = ppd.optionGroups
    for group in groups:
        for opt in group.options:
            values = list(map(lambda x: x["choice"], opt.choices))
            texts = list(map(lambda x: x["text"], opt.choices))
            print("{} = {}".format(opt.keyword, opt.defchoice))
            print("     {}".format(opt.text))
            if values != texts:
                choices = ["{} = {}".format(v, texts[values.index(v)]) for v in values]
                print("     Choices: {}".format(choices[0]))
                for choice in choices[1:]:
                    print("              {}".format(choice))
            else:
                print("     Choices: {}".format(", ".join(values)))

            print()


if __name__ == "__main__":
    main()
