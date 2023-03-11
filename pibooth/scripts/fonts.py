# -*- coding: utf-8 -*-

"""Script to list all installed fonts.
"""

from pibooth.fonts import get_available_fonts
from pibooth.utils import LOGGER, configure_logging, format_columns_words


def main():
    """Application entry point.
    """
    configure_logging()
    LOGGER.info("Listing all fonts available...")
    print("\n".join(format_columns_words(get_available_fonts(), 3)))


if __name__ == "__main__":
    main()
