# -*- coding: utf-8 -*-


from pibooth.plugins.camera_plugin import CameraPlugin
from pibooth.plugins.lights_plugin import LightsPlugin
from pibooth.plugins.picture_plugin import PicturePlugin
from pibooth.plugins.printer_plugin import PrinterPlugin
from pibooth.plugins.view_plugin import ViewPlugin


def get_plugins(*paths):
    """Return the list of internal plugins and load those at the
    given paths.

    note:: by default hooks are called in LIFO registered order thus
           register order may be important.
    """
    return [ViewPlugin(),  # Last called
            PrinterPlugin(),
            PicturePlugin(),
            CameraPlugin(),
            LightsPlugin()]  # First called
