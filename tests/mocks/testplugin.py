# -*- coding: utf-8 -*-

import pibooth

__version__ = "1.2.3"


@pibooth.hookimpl
def pibooth_configure(cfg):
    cfg.set('testplugin', 'configured', 'True')


@pibooth.hookimpl(optionalhook=True)
def optional_hook(cfg):
    cfg.set('testplugin', 'optional_configured', 'True')
