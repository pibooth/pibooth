# -*- coding: utf-8 -*-

from pibooth.utils import LOGGER, load_module
from pibooth.plugins.camera_plugin import CameraPlugin
from pibooth.plugins.lights_plugin import LightsPlugin
from pibooth.plugins.picture_plugin import PicturePlugin
from pibooth.plugins.printer_plugin import PrinterPlugin
from pibooth.plugins.view_plugin import ViewPlugin


def load_plugins(plugin_manager, *paths):
    """Return the list of core plugins and load those from the
    given paths.

    note:: by default hooks are called in LIFO registered order thus
           plugins register order may be important.
    """
    plugins = []
    for path in paths:
        plugin = load_module(path)
        if plugin:
            LOGGER.info("Plugin '%s' loaded", path)
            plugins.append(plugin)

    plugins += [ViewPlugin(plugin_manager),  # Last called
                PrinterPlugin(plugin_manager),
                PicturePlugin(plugin_manager),
                CameraPlugin(plugin_manager),
                LightsPlugin(plugin_manager)]  # First called

    for plugin in plugins:
        plugin_manager.register(plugin)

    # Check that each hookimpl is defined in the hookspec
    # except for hookimpl with kwarg ``optionalhook=True``.
    plugin_manager.check_pending()
