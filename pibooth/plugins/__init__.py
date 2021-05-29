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
        self._plugin2calls = {}

        def before(hook_name, methods, kwargs):
            """Keep the list of already called hook per plugin to know if a
            plugin has already been initialized in case of hot-registration.
            """
            for hookimpl in methods:
                self._plugin2calls[hookimpl.plugin].add(hook_name)

        def after(outcome, hook_name, methods, kwargs):
            pass

        self.add_hookcall_monitoring(before, after)

    def register(self, plugin, name=None):
        """Override to keep all plugins that have already been registered
        at least one time.
        """
        plugin_name = super(PiPluginManager, self).register(plugin, name)
        if plugin not in self._plugin2calls:
            self._plugin2calls[plugin] = set()
        return plugin_name

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

        # Disable unwanted plugins
        if disabled:
            for name in disabled:
                self.unregister(name=name)

    def list_external_plugins(self):
        """Return the list of loaded plugins except ``pibooth`` core plugins.
        (external plugins can be registered or unregistered)

        :return: list of plugins
        :rtype: list
        """
        values = []
        for plugin in self._plugin2calls:
            # The core plugins are classes, we don't want to include
            # them here, thus we take only the modules objects.
            if inspect.ismodule(plugin):
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

    def get_calls_history(self, plugin):
        """Return the ist of the hook names that has already been called at
        least one time fr the given plugins.

        :param plugin: plugin for which calls history is requested
        :type plugin: object
        """
        if plugin in self._plugin2calls:
            return list(self._plugin2calls[plugin])
        return []

    def subset_hook_caller_for_plugin(self, name, plugin):
        """ Return a new :py:class:`.hooks._HookCaller` instance for the named
        method which manages calls to the given plugins."""
        exluded_plugins = [p for p in self.get_plugins() if self.get_name(p) != self.get_name(plugin)]
        return self.subset_hook_caller(name, exluded_plugins)
