# -*- coding: utf-8 -*-

import os.path as osp
from PIL import Image
import pygame
from pibooth.config import PiConfigParser
from pibooth.pictures import maker
from pibooth.pictures import sizing
from pibooth import language
from pibooth import fonts


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
    path = osp.join(osp.dirname(osp.abspath(__file__)), language.CURRENT, name)
    if not osp.isfile(path):
        # Look for common image
        path = osp.join(osp.dirname(osp.abspath(__file__)), 'com', name)
    return path


def get_pygame_image(name, size=None, antialiasing=True, hflip=False, vflip=False, crop=False, angle=0):
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
    :param angle: angle of rotation of the image
    :type angle: int

    :return: pygame.Surface with image
    :rtype: object
    """
    path = get_filename(name)
    if not size:
        image = pygame.image.load(path).convert()
    else:
        if osp.isfile(path):
            pil_image = Image.open(path)
        else:
            pil_image = Image.new('RGBA', size, (255, 0, 0, 0))
        if crop:
            pil_image = pil_image.crop(sizing.new_size_by_croping_ratio(pil_image.size, size))
        pil_image = pil_image.resize(sizing.new_size_keep_aspect_ratio(pil_image.size, size),
                                     Image.ANTIALIAS if antialiasing else Image.NEAREST)
        image = pygame.image.fromstring(pil_image.tobytes(), pil_image.size, pil_image.mode)

    if hflip or vflip:
        image = pygame.transform.flip(image, hflip, vflip)
    if angle != 0:
        image = pygame.transform.rotate(image, angle)
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

def get_layout_image(text_color, layout_number, size):
    """Generate the layout image with the corresponding text
    """
    layout_image = get_pygame_image("layout{0}.png".format(layout_number), size)
    text = language.get_translated_text(str(layout_number))
    pos = (size[0]/2, size[1]*0.85)
    if text:
        rect_x = 0.7*min(2*pos[0], 2*(size[0] - pos[0]))
        rect_y = 0.7*min(2*pos[1], 2*(size[1] - pos[1]))
        text_font = fonts.get_pygame_font(text, fonts.get_filename(fonts.CURRENT), rect_x, rect_y)
        surface = text_font.render(text, True, text_color)
        pos = (pos[0]/2, pos[1])
        layout_image.blit(surface, surface.get_rect(center=pos))
    return layout_image
