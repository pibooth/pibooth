# -*- coding: utf-8 -*-

import os.path as osp
import pygame


def get_filename(name):
    """Return absolute path to a picture located in the current package.
    """
    return osp.join(osp.dirname(osp.abspath(__file__)), name)


def get_image(name):
    """Return a Pygame image.
    """
    return pygame.image.load(get_filename(name)).convert()
