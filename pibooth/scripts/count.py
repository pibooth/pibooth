# -*- coding: utf-8 -*-

"""Script to display/update counters.
"""

import sys
import json
from pibooth.counters import Counters
from pibooth.utils import configure_logging
from pibooth.config import PiConfigParser
from pibooth.plugins import create_plugin_manager


def main():
    """Application entry point.
    """
    configure_logging()
    plugin_manager = create_plugin_manager()
    config = PiConfigParser("~/.config/pibooth/pibooth.cfg", plugin_manager)

    counters = Counters(config.join_path("counters.pickle"),
                        taken=0, printed=0, forgotten=0,
                        remaining_duplicates=config.getint('PRINTER', 'max_duplicates'))

    if '--json' in sys.argv:
        print(json.dumps(counters.data))
    elif '--update' in sys.argv:
        try:
            print("\nUpdating counters (current value in square bracket):\n")
            for name in counters:
                value = input(" -> {:.<18} [{:>4}] : ".format(name.capitalize(), counters[name]))
                if value.strip():
                    setattr(counters, name, int(value))
        except KeyboardInterrupt:
            pass
        print()
    else:
        print("\nListing current counters:\n")
        for name in counters:
            print(" -> {:.<25} : {:>4}".format(name.capitalize(), counters[name]))
        print()


if __name__ == "__main__":
    main()
