# -*- coding: utf-8 -*-

import pytest
import pibooth


class CustomPlugin:

    __name__ = "customplugin"
    __version__ = "1.2.3"

    @pibooth.hookimpl
    def pibooth_configure(self, cfg):
        cfg.set('customplugin', 'configured', 'True')

    @pibooth.hookimpl(optionalhook=True)
    def optional_hook(self, cfg):
        cfg.set('customplugin', 'optional_configured', 'True')


def test_list_extern_plugins(pm):
    assert pm.list_external_plugins() == []
    plugin = CustomPlugin()
    pm.register(plugin)
    assert pm.list_external_plugins() == [plugin]


def test_register(pm, cfg):
    plugin = CustomPlugin()
    pm.register(plugin)
    assert pm.is_registered(plugin)

    pm.subset_hook_caller('pibooth_configure')(cfg=cfg)
    assert cfg.get('customplugin', 'configured') == 'True'


def test_friendly_name(pm):
    plugin = CustomPlugin()
    pm.register(plugin)
    assert pm.get_friendly_name(plugin) == "customplugin-1.2.3"
    assert pm.get_friendly_name(plugin, False) == "customplugin"


def test_load_all_plugins(pm):
    assert not pm.get_plugins()
    pm.load_all_plugins([])
    assert pm.get_plugins()  # Core plugins are loaded
    assert pm.list_external_plugins() == []


def test_load_all_plugins_from_path(pm, cfg, plugin_path):
    assert not pm.get_plugins()
    pm.load_all_plugins([plugin_path])
    assert pm.get_plugin("testplugin")
    assert pm.list_external_plugins()

    pm.subset_hook_caller('pibooth_configure')(cfg=cfg)
    assert cfg.getboolean('testplugin', 'configured')


def test_call_optional_hook(pm, cfg):
    with pytest.raises(AttributeError):
        pm.subset_hook_caller('optional_hook')(cfg=cfg)

    pm.subset_hook_caller('optional_hook', optional=True)(cfg=cfg)
    assert not cfg.has_section('customplugin')

    pm.register(CustomPlugin())

    pm.subset_hook_caller('optional_hook', optional=True)(cfg=cfg)
    assert cfg.getboolean('customplugin', 'optional_configured')


def test_call_history(pm, cfg):
    plugin = CustomPlugin()
    pm.register(plugin)

    assert pm.get_calls_history(plugin) == []
    pm.subset_hook_caller('pibooth_configure')(cfg=cfg)
    assert pm.get_calls_history(plugin) == ['pibooth_configure']


def test_subset_hook_caller_for_plugin(pm, cfg, plugin_path):
    pm.load_all_plugins([plugin_path])
    plugin = CustomPlugin()
    pm.register(plugin)
    hook = pm.subset_hook_caller_for_plugin('pibooth_configure', plugin)
    hook(cfg=cfg)
    assert cfg.getboolean('customplugin', 'configured')
    assert not cfg.has_section('testplugin')
