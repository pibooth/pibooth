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

    return sorted(fonts_list)


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

    # Show system avaiable fonts
    system_fonts = pygame.font.get_fonts()
    most_similar = 0
    most_similar_index = 0
    for i in range(len(system_fonts)):
        # noinspection PyArgumentEqualDefault
        sim = SequenceMatcher(None, system_fonts[i], name).ratio()  # Similarity
        if sim > most_similar:
            most_similar = sim
            most_similar_index = i
    sys_font_sim = system_fonts[most_similar_index]
    raise ValueError('System font "{0}" unknown, maybe you mean "{1}"'.format(name,
                                                                              sys_font_sim))
