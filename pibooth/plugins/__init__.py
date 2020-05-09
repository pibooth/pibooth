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
            LOGGER.debug("Plugin found at '%s'", path)
            plugins.append(plugin)

    plugins += [LightsPlugin(plugin_manager),  # Last called
                ViewPlugin(plugin_manager),
                PrinterPlugin(plugin_manager),
                PicturePlugin(plugin_manager),
                CameraPlugin(plugin_manager)]  # First called

    for plugin in plugins:
        plugin_manager.register(plugin)

    # Check that each hookimpl is defined in the hookspec
    # except for hookimpl with kwarg ``optionalhook=True``.
    plugin_manager.check_pending()


def get_names(plugin_manager):
    """Return the list of registered plugins.
    """
    values = []
    for _plugin, dist in plugin_manager.list_plugin_distinfo():
        name = "{dist.project_name}-{dist.version}".format(dist=dist)
        # Questionable convenience, but it keeps things short
        if name.startswith("pibooth-") or name.startswith("pibooth_"):
            name = name[8:]
        # List Python package names however they can have more
        # than one plugin depending on their architecture.
        if name not in values:
            values.append(name)
    return values
