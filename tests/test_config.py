# -*- coding: utf-8 -*-

import os.path as osp
import pytest


def test_join_path_to_config_directory(cfg):
    assert cfg.join_path() == osp.dirname(cfg.filename)
    assert cfg.join_path('test') == osp.join(osp.dirname(cfg.filename), 'test')


def test_not_in_config_option(cfg):
    assert cfg.get('GENERAL', 'autostart') == 'False'


def test_not_existing_option(cfg):
    with pytest.raises(KeyError):
        cfg.get('GENERAL', 'toto')


def test_string(cfg):
    assert cfg.get('GENERAL', 'language') == 'fr'


def test_color(cfg):
    assert cfg.gettyped('WINDOW', 'text_color') == (255, 255, 255)


def test_boolean(cfg):
    assert cfg.getboolean('WINDOW', 'animate') is False


def test_integer(cfg):
    assert cfg.getint('CONTROLS', 'picture_btn_pin') == 11


def test_float(cfg):
    assert cfg.getfloat('CONTROLS', 'debounce_delay') == 0.3


def test_tuple(cfg):
    assert cfg.gettuple('PICTURE', 'captures', int) == (4, 1)


def test_empty(cfg):
    assert cfg.get('PICTURE', 'overlays') == ''


def test_path_list(cfg):
    dirname = osp.dirname(cfg.filename)
    fullpath = (osp.join(dirname, 'plugin1.py'), osp.join(dirname, 'plugin2.py'))
    assert cfg.gettuple('GENERAL', 'plugins', 'path') == fullpath


def test_color_list(cfg):
    assert cfg.gettuple('PICTURE', 'text_colors', 'color') == ((0, 0, 0), (234, 45, 2))


def test_string_list(cfg):
    assert cfg.gettuple('PICTURE', 'overlays', str) == ()
    assert cfg.gettuple('PICTURE', 'text_fonts', str) == ('Amatic-Bold', 'AmaticSC-Regular')


def test_string_list_extended(cfg):
    assert cfg.gettuple('PICTURE', 'overlays', str, 1) == ('',)
    assert cfg.gettuple('PICTURE', 'backgrounds', str) == ('fond1.jpg', 'fond2.jpg')
    assert cfg.gettuple('PICTURE', 'backgrounds', str, 3) == ('fond1.jpg', 'fond2.jpg', 'fond2.jpg')
