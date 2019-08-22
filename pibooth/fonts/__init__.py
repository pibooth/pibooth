# -*- coding: utf-8 -*-

import os
import fnmatch
import os.path as osp
from difflib import SequenceMatcher
import pygame


EMBEDDED_FONT_PATH = osp.dirname(osp.abspath(__file__))


def get_available_fonts():
    """Return the list of available fonts.
    """
    fonts_list = []
    for font_file in os.listdir(EMBEDDED_FONT_PATH):
        if fnmatch.fnmatch(font_file, '*.ttf'):
            fonts_list.append(osp.splitext(osp.basename(font_file))[0])

    fonts_list.extend(pygame.font.get_fonts())

    return sorted(fonts_list, key=lambda s: s.lower())


def get_filename(name):
    """Return absolute path to a font definition file located in the current
    package.
    """
    if osp.isfile(name):
        return name

    embedded_path = osp.join(osp.dirname(osp.abspath(__file__)), name)
    if embedded_path and osp.isfile(embedded_path):
        return embedded_path

    elif embedded_path and osp.isfile(embedded_path + '.ttf'):
        return embedded_path + '.ttf'

    system_path = pygame.font.match_font(name)
    if system_path and osp.isfile(system_path):
        return system_path

    # Show avaiable fonts
    most_similar = None
    most_similar_ratio = 0
    for font_name in get_available_fonts():
        sim = SequenceMatcher(None, font_name, name).ratio()  # Similarity
        if sim > most_similar_ratio:
            most_similar = font_name
            most_similar_ratio = sim
    raise ValueError('System font "{0}" unknown, maybe you mean "{1}"'.format(name, most_similar))
