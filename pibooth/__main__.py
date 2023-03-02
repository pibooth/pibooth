#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Pibooth entry point.
"""

import tempfile
import logging
import argparse
import os.path as osp
import multiprocessing
from warnings import filterwarnings

from gpiozero import Device, pi_info
from gpiozero.pins.mock import MockFactory
from gpiozero.exc import BadPinFactory, PinFactoryFallback

import pibooth
from pibooth.app import PiboothApplication
from pibooth import language
from pibooth.utils import LOGGER, configure_logging
from pibooth.plugins import create_plugin_manager
from pibooth.config import PiboothConfigParser


# Set the default pin factory to a mock factory if pibooth is not started a Raspberry Pi
try:
    filterwarnings("ignore", category=PinFactoryFallback)
    GPIO_INFO = "on Raspberry pi {0}".format(pi_info().model)
except BadPinFactory:
    Device.pin_factory = MockFactory()
    GPIO_INFO = "without physical GPIO, fallback to GPIO mock"


def main():
    """Application entry point.
    """
    if hasattr(multiprocessing, 'set_start_method'):
        # Avoid use 'fork': safely forking a multithreaded process is problematic
        multiprocessing.set_start_method('spawn')

    parser = argparse.ArgumentParser(usage="%(prog)s [options]", description=pibooth.__doc__)

    parser.add_argument("config_directory", nargs='?', default="~/.config/pibooth",
                        help=u"path to configuration directory (default: %(default)s)")

    parser.add_argument('--version', action='version', version=pibooth.__version__,
                        help=u"show program's version number and exit")

    parser.add_argument("--config", action='store_true',
                        help=u"edit the current configuration and exit")

    parser.add_argument("--translate", action='store_true',
                        help=u"edit the GUI translations and exit")

    parser.add_argument("--reset", action='store_true',
                        help=u"restore the default configuration/translations and exit")

    parser.add_argument("--nolog", action='store_true', default=False,
                        help=u"don't save console output in a file (avoid filling the /tmp directory)")

    parser.add_argument("--nogui", dest='gui', action='store_const', const='nogui',
                        help=u"don't show Graphical User Interface", default='pygame')

    parser.add_argument("--noplugin", action='store_true', default=False,
                        help=u"don't load external plugins")

    parser.add_argument("--profile", action='store_true',
                        help=u"run the profiler to do CPU times analysis")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("-v", "--verbose", dest='logging', action='store_const', const=logging.DEBUG,
                       help=u"report more information about operations", default=logging.INFO)
    group.add_argument("-q", "--quiet", dest='logging', action='store_const', const=logging.WARNING,
                       help=u"report only errors and warnings", default=logging.INFO)

    options = parser.parse_args()

    if not options.nolog:
        filename = osp.join(tempfile.gettempdir(), 'pibooth.log')
    else:
        filename = None
    configure_logging(options.logging, '[ %(levelname)-8s] %(name)-18s: %(message)s', filename=filename)

    plugin_manager = create_plugin_manager()

    # Load the configuration
    config = PiboothConfigParser(osp.join(options.config_directory, "pibooth.cfg"), plugin_manager, not options.reset)

    # Register plugins
    plugin_manager.load_all_plugins(config.gettuple('GENERAL', 'plugins', 'path'),
                                    'all' if options.noplugin else config.gettuple('GENERAL', 'plugins_disabled', str))
    LOGGER.info("Installed plugins: %s", ", ".join(
        [plugin_manager.get_friendly_name(p) for p in plugin_manager.list_external_plugins()]))

    # Load the languages
    language.init(config.join_path("translations.cfg"), options.reset)

    # Update configuration with plugins ones
    plugin_manager.hook.pibooth_configure(cfg=config)

    # Ensure config files are present in case of first pibooth launch
    if not options.reset:
        if not osp.isfile(config.filename):
            config.save(default=True)
        plugin_manager.hook.pibooth_reset(cfg=config, hard=False)

    if options.config:
        LOGGER.info("Editing the pibooth configuration...")
        config.edit()
    elif options.translate:
        LOGGER.info("Editing the GUI translations...")
        language.edit()
    elif options.reset:
        config.save(default=True)
        plugin_manager.hook.pibooth_reset(cfg=config, hard=True)
    else:
        LOGGER.info("Starting the photo booth application %s", GPIO_INFO)
        app = PiboothApplication(config, plugin_manager, options.gui)
        app.exec(options.profile)


if __name__ == '__main__':
    main()
