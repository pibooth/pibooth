# -*- coding: utf-8 -*-

import os.path as osp
from PIL import Image
import pygame
from pibooth.config import PiConfigParser
from pibooth.pictures import maker
from pibooth.pictures import sizing


AUTO = 'auto'
PORTRAIT = 'portrait'
LANDSCAPE = 'landscape'


def get_filename(name):
    """Return absolute path to a picture located in the current package.

    :param name: name of an image located in language folders
    :type name: str

    :return: absolute image path
    :rtype: str
    """
    path = osp.join(osp.dirname(osp.abspath(__file__)), PiConfigParser.language, name)
    if not osp.isfile(path):
        # Look for common image
        return osp.join(osp.dirname(osp.abspath(__file__)), 'com', name)
    return path


def get_pygame_image(name, size=None, antialiasing=True, hflip=False, vflip=False, crop=False):
    """Return a Pygame image. If a size is given, the image is
    resized keeping the original image's aspect ratio.

    :param name: name of an image located in language folders
    :type name: str
    :param size: resize image to this size
    :type size: tuple
    :param antialiasing: use antialiasing algorithm when resize
    :type antialiasing: bool
    :param hflip: apply an horizontal flip
    :type hflip: bool
    :param vflip: apply a vertical flip
    :type vflip: bool
    :param crop: crop image to fit aspect ration of the size
    :type crop: bool

    :return: pygame.Surface with image
    :rtype: object
    """
    if not size:
        image = pygame.image.load(get_filename(name)).convert()
    else:
        image = Image.open(get_filename(name))
        if crop:
            image = image.crop(sizing.new_size_by_croping_ratio(image.size, size))
        image = image.resize(sizing.new_size_keep_aspect_ratio(image.size, size),
                             Image.ANTIALIAS if antialiasing else Image.NEAREST)
        image = pygame.image.fromstring(image.tobytes(), image.size, image.mode)

    if hflip or vflip:
        image = pygame.transform.flip(image, hflip, vflip)
    return image


def get_best_orientation(captures):
    """Return the most adapted orientation (PORTRAIT or LANDSCAPE),
    depending on the resolution of the given captures.

    It use the size of the first capture to determine the orientation.

    :param captures: list of captures to concatenate
    :type captures: list

    :return: orientation PORTRAIT or LANDSCAPE
    :rtype: str
    """
    is_portrait = captures[0].size[0] < captures[0].size[1]
    if len(captures) == 1 or len(captures) == 4:
        if is_portrait:
            orientation = PORTRAIT
        else:
            orientation = LANDSCAPE
    elif len(captures) == 2 or len(captures) == 3:
        if is_portrait:
            orientation = LANDSCAPE
        else:
            orientation = PORTRAIT
    else:
        raise ValueError("List of max 4 pictures expected, got {}".format(len(captures)))
    return orientation


def get_picture_maker(captures, orientation=AUTO, paper_format=(4, 6), force_pil=False):
    """Return the picture maker use to concatenate the captures.

    :param captures: list of captures to concatenate
    :type captures: list
    :param orientation: paper orientation
    :type orientation: str
    :param paper_format: paper size in inches
    :type paper_format: tuple
    :param force_pil: force use PIL implementation
    :type force_pil: bool
    """
    assert orientation in (AUTO, PORTRAIT, LANDSCAPE), "Unknown orientation '{}'".format(orientation)
    if orientation == AUTO:
        orientation = get_best_orientation(captures)

    # Ensure paper format is given in portrait (don't manage orientation with it)
    if paper_format[0] > paper_format[1]:
        paper_format = (paper_format[1], paper_format[0])

    # Consider a resolution of 600 dpi
    size = (paper_format[0] * 600, paper_format[1] * 600)
    if orientation == LANDSCAPE:
        size = (size[1], size[0])

    if not maker.cv2 or force_pil:
        return maker.PilPictureMaker(size[0], size[1], *captures)
    else:
        return maker.OpenCvPictureMaker(size[0], size[1], *captures)
