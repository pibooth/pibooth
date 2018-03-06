# -*- coding: utf-8 -*-

import os.path as osp
from PIL import Image
import pygame
from pibooth.config import PtbConfigParser


def get_filename(name):
    """Return absolute path to a picture located in the current package.
    """
    return osp.join(osp.dirname(osp.abspath(__file__)), PtbConfigParser.language, name)


def resize_keep_aspect_ratio(original_size, target_size, resize_type='inner'):
    """Return a new size included (if 'inner') or excluded (if 'outer') in the
    targeted one by resizing and keeping the original image's aspect ratio.
    """
    # Get current and desired ratio for the images
    img_ratio = original_size[0] / float(original_size[1])
    ratio = target_size[0] / float(target_size[1])

    ix, iy = original_size
    if ratio > img_ratio:
        # fit to width
        scale_factor = target_size[0] / float(ix)
        sy = scale_factor * iy
        if sy > target_size[1] and resize_type == 'inner':
            scale_factor = target_size[1] / float(iy)
            sx = scale_factor * ix
            sy = target_size[1]
        else:
            sx = target_size[0]
    elif ratio < img_ratio:
        # fit to height
        scale_factor = target_size[1] / float(iy)
        sx = scale_factor * ix
        if sx > target_size[0] and resize_type == 'inner':
            scale_factor = target_size[0] / float(ix)
            sx = target_size[0]
            sy = scale_factor * iy
        else:
            sy = target_size[1]
    else:
        return target_size
    return (int(sx), int(sy))


def crop_to_size(original_size, target_size, crop_type='middle'):
    """Return a new size included in the target one by croping and
    keeping the original image's aspect ratio.
    """
    if crop_type.endswith('left'):
        x = 0
    elif crop_type.endswith('middle'):
        x = (original_size[0] - target_size[0]) // 2
    elif crop_type.endswith('right'):
        x = original_size[0] - target_size[0]

    if crop_type.startswith('top'):
        y = 0
    elif crop_type.startswith('middle'):
        y = (original_size[1] - target_size[1]) // 2
    elif crop_type.startswith('bottom'):
        y = original_size[1] - target_size[1]

    return (x, y, target_size[0] + x, target_size[1] + y)


def get_image(name, size=None, antialiasing=True):
    """Return a Pygame image. If a size is given, the image is
    resized keeping the original image's aspect ratio.

    :param antialiasing: use antialiasing algorithm when resize
    """
    if not size:
        return pygame.image.load(get_filename(name)).convert()
    else:
        image = Image.open(get_filename(name))
        image = image.resize(resize_keep_aspect_ratio(image.size, size),
                             Image.ANTIALIAS if antialiasing else Image.NEAREST)
        return pygame.image.fromstring(image.tobytes(), image.size, image.mode)
