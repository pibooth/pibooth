# -*- coding: utf-8 -*-

import os.path as osp
import pygame


def get_filename(name):
    """Return absolute path to a picture located in the current package.
    """
    return osp.join(osp.dirname(osp.abspath(__file__)), name)


def get_image(name, size=None):
    """Return a Pygame image. If a size is given, the image is
    resized keeping the original image's aspect ratio.
    """
    image = pygame.image.load(get_filename(name)).convert()
    if size:
        ix, iy = image.get_size()
        if ix > iy:
            # fit to width
            scale_factor = size[0] / float(ix)
            sy = scale_factor * iy
            if sy > size[1]:
                scale_factor = size[1] / float(iy)
                sx = scale_factor * ix
                sy = size[1]
            else:
                sx = size[0]
        else:
            # fit to height
            scale_factor = size[1] / float(iy)
            sx = scale_factor * ix
            if sx > size[0]:
                scale_factor = size[0] / float(ix)
                sx = size[0]
                sy = scale_factor * iy
            else:
                sy = size[1]

        image = pygame.transform.scale(image, (int(sx), int(sy)))
    return image
