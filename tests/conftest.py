# -*- coding: utf-8 -*-


import os
import pytest
from PIL import Image

CAPTURES_DIR = os.path.join(os.path.dirname(__file__), 'captures')


@pytest.fixture
def captures_portrait():
    return [Image.open(os.path.join(CAPTURES_DIR, 'portrait', img))
            for img in os.listdir(os.path.join(CAPTURES_DIR, 'portrait'))]


@pytest.fixture
def captures_landscape():
    return [Image.open(os.path.join(CAPTURES_DIR, 'landscape', img))
            for img in os.listdir(os.path.join(CAPTURES_DIR, 'landscape'))]


@pytest.fixture
def fond():
    return os.path.join(CAPTURES_DIR, 'fond.jpg')
