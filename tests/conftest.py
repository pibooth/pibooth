# -*- coding: utf-8 -*-


import os
import pytest
from PIL import Image
from pibooth.config.parser import PiConfigParser

MOCKS_DIR = os.path.join(os.path.dirname(__file__), 'mocks')
CAPTURES_DIR = os.path.join(os.path.dirname(__file__), 'captures')


@pytest.fixture(scope='session')
def captures_portrait():
    return [Image.open(os.path.join(CAPTURES_DIR, 'portrait', img))
            for img in os.listdir(os.path.join(CAPTURES_DIR, 'portrait'))]


@pytest.fixture(scope='session')
def captures_landscape():
    return [Image.open(os.path.join(CAPTURES_DIR, 'landscape', img))
            for img in os.listdir(os.path.join(CAPTURES_DIR, 'landscape'))]


@pytest.fixture(scope='session')
def fond_path():
    return os.path.join(CAPTURES_DIR, 'fond.jpg')


@pytest.fixture(scope='session')
def overlay_path():
    return os.path.join(CAPTURES_DIR, 'overlay.png')


@pytest.fixture(scope='session')
def cfg_path():
    return os.path.join(MOCKS_DIR, 'pibooth.cfg')

@pytest.fixture(scope='session')
def cfg(cfg_path):
    return PiConfigParser(cfg_path, None)
