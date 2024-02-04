# -*- coding: utf-8 -*-

import os
import os.path as osp
import fnmatch
from difflib import SequenceMatcher
import pygame
from PIL import ImageFont, ImageDraw


EMBEDDED_FONT_PATH = osp.dirname(osp.abspath(__file__))

ALIGN_TOP_LEFT = 'top-left'
ALIGN_TOP_CENTER = 'top-center'
ALIGN_TOP_RIGHT = 'top-right'
ALIGN_CENTER_LEFT = 'center-left'
ALIGN_CENTER = 'center'
ALIGN_CENTER_RIGHT = 'center-right'
ALIGN_BOTTOM_LEFT = 'bottom-left'
ALIGN_BOTTOM_CENTER = 'bottom-center'
ALIGN_BOTTOM_RIGHT = 'bottom-right'


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

    # Show available fonts
    most_similar = None
    most_similar_ratio = 0
    for font_name in get_available_fonts():
        sim = SequenceMatcher(None, font_name, name).ratio()  # Similarity
        if sim > most_similar_ratio:
            most_similar = font_name
            most_similar_ratio = sim
    raise ValueError(f"System font '{name}' unknown, maybe you mean '{most_similar}'")


CURRENT = get_filename('Amatic-Bold')  # Dynamically re-set at startup


def get_pil_font(text, font_name, max_width, max_height):
    """Create the PIL font object which fit the text to the given rectangle.

    :param text: text to draw
    :type text: str
    :param font_name: name or path to font definition file
    :type font_name: str
    :param max_width: width of the rect to fit
    :type max_width: int
    :param max_height: height of the rect to fit
    :type max_height: int

    :return: PIL.Font instance
    :rtype: object
    """
    start, end, k = 0, int(max_height * 2), 0
    while start < end:
        previous_k = k
        k = (start + end) // 2
        font = ImageFont.truetype(font_name, k)
        _left, _top, right, bottom = font.getbbox(text)
        if right > max_width or bottom > max_height:
            end = k
        else:
            if k + 1 == previous_k:
                # Next size may have been tested just too big
                break
            start = k + 1
        del font  # Run garbage collector, to avoid opening too many files
    return ImageFont.truetype(font_name, start)


def get_pygame_font(text, font_name, max_width, max_height):
    """Create the pygame font object which fit the text to the given rectangle.

    :param text: text to draw
    :type text: str
    :param font_name: name or path to font definition file
    :type font_name: str
    :param max_width: width of the rect to fit
    :type max_width: int
    :param max_height: height of the rect to fit
    :type max_height: int

    :return: pygame.Font instance
    :rtype: object
    """
    start, end, k = 0, int(max_height * 2), 0
    while start < end:
        previous_k = k
        k = (start + end) // 2
        font = pygame.font.Font(get_filename(font_name), k)
        font_size = font.size(text)
        if font_size[0] >= max_width or font_size[1] >= max_height:
            end = k
        else:
            if k + 1 == previous_k:
                # Next size may have been tested just too big
                break
            start = k + 1
        del font  # Run garbage collector, to avoid opening too many files
    return pygame.font.Font(get_filename(font_name), start)


def write_on_pil_image(image, text, posx=0, posy=0, max_width=None, max_height=None, font_name=CURRENT, color='black', align=ALIGN_CENTER):
    """Write a text on a PIL image that fit the given image or optional box.

    :param image: PIL.Image instance
    :type image: object
    :param text: text to write
    :type text: str
    :param posx: horizontal position (origin is image top left corner)
    :type posx: int
    :param posy: vertical position (origin is image top left corner)
    :type posy: int
    :param max_width: width of the bounding box
    :type max_width: int
    :param max_height: height of the bounding box
    :type max_height: int
    :param font_name: TrueType front path
    :type font_name: str
    :param color: color of the pen
    :type color: str or tuple
    :param align: text alignment
    :type align: str

    :return: None
    :rtype: None
    """
    draw = ImageDraw.Draw(image)
    if not max_width:
        max_width = image.size[0]
    if not max_height:
        max_height = image.size[1]

    font = get_pil_font(text, font_name, max_width, max_height)
    left, top, right, bottom = font.getbbox(text)
    if align == ALIGN_CENTER:
        posx += (max_width - right) // 2
    elif align == ALIGN_CENTER_RIGHT:
        posx += (max_width - right)
    draw.text((posx - left // 2, posy + (max_height - bottom) // 2 - top // 2), text, color, font=font)
