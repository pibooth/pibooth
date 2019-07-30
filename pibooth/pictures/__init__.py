# -*- coding: utf-8 -*-

import os.path as osp
from PIL import Image
import pygame
from pibooth.config.parser import PiConfigParser
from pibooth.pictures import sizing


def get_filename(name):
    """Return absolute path to a picture located in the current package.
    """
    path = osp.join(osp.dirname(osp.abspath(__file__)), PiConfigParser.language, name)
    if not osp.isfile(path):
        # Look for common image
        return osp.join(osp.dirname(osp.abspath(__file__)), 'com', name)
    return path


def get_image(name, size=None, antialiasing=True, hflip=False, vflip=False):
    """Return a Pygame image. If a size is given, the image is
    resized keeping the original image's aspect ratio.

    :param antialiasing: use antialiasing algorithm when resize
    """
    if not size:
        image = pygame.image.load(get_filename(name)).convert()
    else:
        image = Image.open(get_filename(name))
        image = image.resize(sizing.new_size_keep_aspect_ratio(image.size, size),
                             Image.ANTIALIAS if antialiasing else Image.NEAREST)
        image = pygame.image.fromstring(image.tobytes(), image.size, image.mode)

    if hflip or vflip:
        image = pygame.transform.flip(image, hflip, vflip)
    return image
