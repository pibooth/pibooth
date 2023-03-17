# -*- coding: utf-8 -*-

"""Script to display/update counters.
"""

import sys
import json
from pibooth.counters import Counters
from pibooth.utils import configure_logging
from pibooth.config import PiboothConfigParser
from pibooth.plugins import create_plugin_manager


def main():
    """Application entry point.
    """
    configure_logging()
    plugin_manager = create_plugin_manager()
    config = PiboothConfigParser("~/.config/pibooth/pibooth.cfg", plugin_manager)

    counters = Counters(config.join_path("counters.pickle"),
                        taken=0, printed=0, forgotten=0,
                        remaining_duplicates=config.getint('PRINTER', 'max_duplicates'))

    if '--json' in sys.argv:
        print(json.dumps(counters.data))
    elif '--update' in sys.argv:
        try:
            print("\nUpdating counters (current value in square bracket):\n")
            for name in counters:
                value = input(f" -> {name.capitalize():.<20} [{counters[name]:>4}] : ")
                if value.strip():
                    setattr(counters, name, int(value))
        except KeyboardInterrupt:
            pass
        print()
    else:
        print("\nListing current counters:\n")
        for name in counters:
            print(f" -> {name.capitalize():.<27} : {counters[name]:>4}")
        print()


if __name__ == "__main__":
    main()
