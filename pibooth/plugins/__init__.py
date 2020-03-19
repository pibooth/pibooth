# -*- coding: utf-8 -*-

from pibooth.utils import LOGGER, load_module
from pibooth.plugins.camera_plugin import CameraPlugin
from pibooth.plugins.lights_plugin import LightsPlugin
from pibooth.plugins.picture_plugin import PicturePlugin
from pibooth.plugins.printer_plugin import PrinterPlugin
from pibooth.plugins.view_plugin import ViewPlugin


def get_plugins(*paths):
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

    return plugins + [ViewPlugin(),  # Last called
                      PrinterPlugin(),
                      PicturePlugin(),
                      CameraPlugin(),
                      LightsPlugin()]  # First called
