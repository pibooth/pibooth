# -*- coding: utf-8 -*-

import os
import sys
import shutil
import os.path as osp
import pytest

from pibooth.config import parser
from pibooth.config.parser import PiboothConfigParser, desktop_quote, get_launch_command


@pytest.fixture
def autostart_cfg(cfg_path, pm, tmpdir, monkeypatch):
    """Return a config with autostart enabled and the auto-startup file it
    generates in an isolated directory.
    """
    monkeypatch.setattr(parser, 'get_launch_command', lambda: '/venv/bin/pibooth')
    config = PiboothConfigParser(cfg_path, pm)
    config.autostart_filename = str(tmpdir.join('.config', 'autostart', 'pibooth.desktop'))
    config.set('GENERAL', 'autostart', 'True')
    return config, tmpdir.join('.config', 'autostart', 'pibooth.desktop')


def test_join_path_to_config_directory(cfg):
    assert cfg.join_path() == osp.dirname(cfg.filename)
    assert cfg.join_path('test') == osp.join(osp.dirname(cfg.filename), 'test')


def test_not_in_config_option(cfg):
    assert cfg.get('GENERAL', 'debug') == 'False'
    assert cfg.get('OTHER', 'toto') == 'is a hero'


def test_not_existing_option(cfg):
    with pytest.raises(KeyError):
        cfg.get('HELLO', 'world')


def test_save(cfg):
    with pytest.raises(KeyError):
        cfg.get('HELLO', 'world')
    cfg.set('HELLO', 'world', "beautiful")
    cfg.save()
    cfg.load(clean=True)
    assert cfg.get('HELLO', 'world') == "beautiful"
    assert cfg.get('OTHER', 'toto') == 'is a hero'


def test_save_default(cfg):
    cfg.set('GENERAL', 'autostart_delay', '10')
    assert cfg.get('GENERAL', 'autostart_delay') == '10'
    cfg.save(default=True)
    cfg.load(clean=True)
    assert cfg.get('GENERAL', 'autostart_delay') == '0'
    with pytest.raises(KeyError):
        cfg.get('OTHER', 'toto')


def test_handle_autostart(cfg):
    cfg.handle_autostart()
    assert osp.isfile(cfg.autostart_filename)


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


def test_add_option(cfg):
    with pytest.raises(KeyError):
        cfg.get('HELLO', 'world')
    cfg.add_option('HELLO', 'world', "beautiful", "This is a new dummy option")
    assert cfg.get('HELLO', 'world') == "beautiful"


@pytest.mark.parametrize('path', ['/usr/local/bin/pibooth', '/home/pi/pibooth-venv/bin/pibooth'])
def test_desktop_quote_usual_path(path):
    assert desktop_quote(path) == path


def test_desktop_quote_reserved_character():
    assert desktop_quote('/home/my pi/venv/bin/pibooth') == '"/home/my pi/venv/bin/pibooth"'
    assert desktop_quote("/home/o'pi/venv/bin/pibooth") == '"/home/o\'pi/venv/bin/pibooth"'


def test_desktop_quote_escaped_character():
    assert desktop_quote('/home/a"b/pibooth') == '"/home/a\\"b/pibooth"'
    assert desktop_quote('/home/a\\b/pibooth') == '"/home/a\\\\b/pibooth"'
    assert desktop_quote('/home/a`b/pibooth') == '"/home/a\\`b/pibooth"'
    assert desktop_quote('/home/a$b/pibooth') == '"/home/a\\$b/pibooth"'


def test_desktop_quote_percent_sign():
    assert desktop_quote('/home/100%/bin/pibooth') == '/home/100%%/bin/pibooth'
    assert desktop_quote('/home/100% pi/bin/pibooth') == '"/home/100%% pi/bin/pibooth"'


def test_get_launch_command_next_to_interpreter(tmpdir, monkeypatch):
    script = tmpdir.join('bin', 'pibooth')
    script.write('', ensure=True)
    monkeypatch.setattr(sys, 'executable', str(tmpdir.join('bin', 'python')))
    assert get_launch_command() == str(script)


def test_get_launch_command_from_path(tmpdir, monkeypatch):
    monkeypatch.setattr(sys, 'executable', str(tmpdir.join('bin', 'python')))
    monkeypatch.setattr(shutil, 'which', lambda name: '/usr/bin/' + name)
    assert get_launch_command() == '/usr/bin/pibooth'


def test_get_launch_command_not_resolved(tmpdir, monkeypatch):
    monkeypatch.setattr(sys, 'executable', str(tmpdir.join('bin', 'python')))
    monkeypatch.setattr(shutil, 'which', lambda name: None)
    assert get_launch_command() == 'pibooth'


def test_autostart_file_generated(autostart_cfg):
    config, desktop_file = autostart_cfg
    config.handle_autostart()
    assert desktop_file.read() == ("[Desktop Entry]\n"
                                   "Name=pibooth\n"
                                   "Exec=/venv/bin/pibooth\n"
                                   "Type=application\n")


def test_autostart_file_generated_with_delay(autostart_cfg):
    config, desktop_file = autostart_cfg
    config.set('GENERAL', 'autostart_delay', '5')
    config.handle_autostart()
    assert 'Exec=bash -c "sleep 5 && /venv/bin/pibooth"\n' in desktop_file.read()


def test_autostart_file_quotes_path_with_space(autostart_cfg, monkeypatch):
    config, desktop_file = autostart_cfg
    monkeypatch.setattr(parser, 'get_launch_command', lambda: '/home/my pi/venv/bin/pibooth')
    config.handle_autostart()
    assert 'Exec="/home/my pi/venv/bin/pibooth"\n' in desktop_file.read()

    config.set('GENERAL', 'autostart_delay', '5')
    config.handle_autostart()
    assert 'Exec=bash -c "sleep 5 && \'/home/my pi/venv/bin/pibooth\'"\n' in desktop_file.read()


def test_autostart_file_regenerated_on_command_change(autostart_cfg, monkeypatch):
    config, desktop_file = autostart_cfg
    config.handle_autostart()
    monkeypatch.setattr(parser, 'get_launch_command', lambda: '/other/venv/bin/pibooth')
    config.handle_autostart()
    assert 'Exec=/other/venv/bin/pibooth\n' in desktop_file.read()


def test_autostart_file_regenerated_from_bare_command(autostart_cfg):
    config, desktop_file = autostart_cfg
    desktop_file.write("[Desktop Entry]\nName=pibooth\nExec=pibooth\nType=application\n", ensure=True)
    config.handle_autostart()
    assert 'Exec=/venv/bin/pibooth\n' in desktop_file.read()


def test_autostart_file_regenerated_on_delay_prefix_change(autostart_cfg):
    config, desktop_file = autostart_cfg
    config.set('GENERAL', 'autostart_delay', '50')
    config.handle_autostart()
    config.set('GENERAL', 'autostart_delay', '5')
    config.handle_autostart()
    assert 'sleep 5 &&' in desktop_file.read()


def test_autostart_file_left_untouched(autostart_cfg):
    config, desktop_file = autostart_cfg
    config.handle_autostart()
    os.utime(str(desktop_file), (0, 0))
    config.handle_autostart()
    assert desktop_file.stat().mtime == 0


def test_autostart_file_removed(autostart_cfg):
    config, desktop_file = autostart_cfg
    config.handle_autostart()
    config.set('GENERAL', 'autostart', 'False')
    config.handle_autostart()
    assert not desktop_file.check()
