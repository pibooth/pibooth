# -*- coding: utf-8 -*-

import inspect
import pluggy

from pibooth.utils import LOGGER, load_module
from pibooth.plugins import hookspecs
from pibooth.plugins.camera_plugin import CameraPlugin
from pibooth.plugins.lights_plugin import LightsPlugin
from pibooth.plugins.picture_plugin import PicturePlugin
from pibooth.plugins.printer_plugin import PrinterPlugin
from pibooth.plugins.view_plugin import ViewPlugin


def create_plugin_manager():
    """Create plugin manager and defined hooks specification."""
    plugin_manager = pluggy.PluginManager(hookspecs.hookspec.project_name)
    plugin_manager.add_hookspecs(hookspecs)
    plugin_manager.load_setuptools_entrypoints(hookspecs.hookspec.project_name)
    return plugin_manager


def load_plugins(plugin_manager, *paths):
    """Register the core plugins and load those from the given paths.

    note:: by default hooks are called in LIFO registered order thus
           plugins register order is important.

    :param plugin_manager: plugins manager instance
    :type plugin_manager: :py:class:`pluggy.PluginManager`
    :param paths: list of Python module paths to load
    :type paths: str
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
    # except for hookimpl with kwarg 'optionalhook=True'.
    plugin_manager.check_pending()


def list_plugin_names(plugin_manager):
    """Return the list of registered plugins.

    :param plugin_manager: plugins manager instance
    :type plugin_manager: :py:class:`pluggy.PluginManager`
    """
    values = []
    for plugin in plugin_manager.get_plugins():
        # The core plugins are classes, we don't want to include
        # them here, thus we take only the modules objects.
        if inspect.ismodule(plugin):
            name = get_plugin_name(plugin_manager, plugin)
            if name not in values:
                values.append(name)
    return values


def get_plugin_name(plugin_manager, plugin, version=True):
    """Return the canonical name of the given plugin and
    optionally sits version.

    :param plugin_manager: plugins manager instance
    :type plugin_manager: :py:class:`pluggy.PluginManager`
    :param plugin: registered plugin object
    :type plugin: object
    :param version: include the version number
    :type version: bool
    """
    # List of all setuptools registered plugins
    distinfo = dict(plugin_manager.list_plugin_distinfo())

    if plugin in distinfo:
        name = distinfo[plugin].project_name
        vnumber = distinfo[plugin].version
    else:
        name = plugin_manager.get_name(plugin)
        if not name:
            name = getattr(plugin, '__name__', "unknown")
        vnumber = getattr(plugin, '__version__', '?.?.?')

    if version:
        name = "{}-{}".format(name, vnumber)
    else:
        name = "{}".format(name)

    # Questionable convenience, but it keeps things short
    if name.startswith("pibooth-") or name.startswith("pibooth_"):
        name = name[8:]

    return name
