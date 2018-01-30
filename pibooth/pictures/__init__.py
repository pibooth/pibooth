# -*- coding: utf-8 -*-

import os.path as osp
from PIL import Image
import pygame
from pibooth.config import PtbConfigParser


def get_filename(name):
    """Return absolute path to a picture located in the current package.
    """
    return osp.join(osp.dirname(osp.abspath(__file__)), PtbConfigParser.language, name)


def resize_keep_aspect_ratio(original_size, target_size):
    """Return a new size included in the target one and
    keeping the original image's aspect ratio.
    """
    ix, iy = original_size
    if ix > iy:
        # fit to width
        scale_factor = target_size[0] / float(ix)
        sy = scale_factor * iy
        if sy > target_size[1]:
            scale_factor = target_size[1] / float(iy)
            sx = scale_factor * ix
            sy = target_size[1]
        else:
            sx = target_size[0]
    else:
        # fit to height
        scale_factor = target_size[1] / float(iy)
        sx = scale_factor * ix
        if sx > target_size[0]:
            scale_factor = target_size[0] / float(ix)
            sx = target_size[0]
            sy = scale_factor * iy
        else:
            sy = target_size[1]
    return (int(sx), int(sy))


def get_image(name, size=None):
    """Return a Pygame image. If a size is given, the image is
    resized keeping the original image's aspect ratio.
    """
    if not size:
        return pygame.image.load(get_filename(name)).convert()

    image = Image.open(get_filename(name))
    image = image.resize(resize_keep_aspect_ratio(image.size, size), Image.ANTIALIAS)
    return pygame.image.fromstring(image.tobytes(), image.size, image.mode)
