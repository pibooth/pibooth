# -*- coding: utf-8 -*-

import os.path as osp
from PIL import Image
import pygame
from pibooth.config import PtbConfigParser
from pibooth.pictures import sizing


def get_filename(name):
    """Return absolute path to a picture located in the current package.
    """
    return osp.join(osp.dirname(osp.abspath(__file__)), PtbConfigParser.language, name)


def get_image(name, size=None, antialiasing=True):
    """Return a Pygame image. If a size is given, the image is
    resized keeping the original image's aspect ratio.

    :param antialiasing: use antialiasing algorithm when resize
    """
    if not size:
        return pygame.image.load(get_filename(name)).convert()
    else:
        image = Image.open(get_filename(name))
        image = image.resize(sizing.new_size_keep_aspect_ratio(image.size, size),
                             Image.ANTIALIAS if antialiasing else Image.NEAREST)
        return pygame.image.fromstring(image.tobytes(), image.size, image.mode)
