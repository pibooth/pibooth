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
    plugin_manager = PiPluginManager(hookspecs.hookspec.project_name)
    plugin_manager.add_hookspecs(hookspecs)
    return plugin_manager


class PiPluginManager(pluggy.PluginManager):

    def __init__(self, *args, **kwargs):
        super(PiPluginManager, self).__init__(*args, **kwargs)
        self._loaded_plugins = {}

    def load_all_plugins(self, paths, disabled=None):
        """Register the core plugins, load plugins from setuptools entry points
        and the load given module/package paths.

        note:: by default hooks are called in LIFO registered order thus
               plugins register order is important.

        :param paths: list of Python module/package paths to load
        :type paths: list
        :param disabled: list of plugins name to be disabled after loaded
        :type disabled: list
        """
        # Load plugins declared by setuptools entry points
        self.load_setuptools_entrypoints(hookspecs.hookspec.project_name)

        plugins = []
        for path in paths:
            plugin = load_module(path)
            if plugin:
                LOGGER.debug("Plugin found at '%s'", path)
                plugins.append(plugin)

        plugins += [LightsPlugin(self),  # Last called
                    ViewPlugin(self),
                    PrinterPlugin(self),
                    PicturePlugin(self),
                    CameraPlugin(self)]  # First called

        for plugin in plugins:
            self.register(plugin)

        # Check that each hookimpl is defined in the hookspec
        # except for hookimpl with kwarg 'optionalhook=True'.
        self.check_pending()

        # Keep the reference of loaded plugins
        self._loaded_plugins = list(self._name2plugin.values())

        # Disable unwanted plugins
        if disabled:
            for name in disabled:
                self.unregister(name)

    def list_extern_plugins(self):
        """Return the list of loaded plugins except ``pibooth`` core plugins.
        (can be registered or unregistered)

        :return: list of plugins
        :rtype: list
        """
        values = []
        for plugin in self._loaded_plugins:
            # The core plugins are classes, we don't want to include
            # them here, thus we take only the modules objects.
            if inspect.ismodule(plugin):
                plugin.fullname = self.get_friendly_name(plugin)
                if plugin not in values:
                    values.append(plugin)
        return values

    def get_friendly_name(self, plugin, version=True):
        """Return the friendly name of the given plugin and
        optionally its version.

        :param plugin: registered plugin object
        :type plugin: object
        :param version: include the version number
        :type version: bool
        """
        # List of all setuptools registered plugins
        distinfo = dict(self.list_plugin_distinfo())

        if plugin in distinfo:
            name = distinfo[plugin].project_name
            vnumber = distinfo[plugin].version
        else:
            name = self.get_name(plugin)
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
