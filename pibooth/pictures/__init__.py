# -*- coding: utf-8 -*-

import os.path as osp
from PIL import Image, ImageOps
import pygame
from pibooth import language
from pibooth import fonts
from pibooth.pictures import factory
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
    return osp.join(osp.dirname(osp.abspath(__file__)), 'assets', name)


def colorize_pil_image(pil_image, color, bg_color=None):
    """Convert a picto in white to the corresponding color.

    :param pil_image: PIL image to be colorized
    :type pil_image: :py:class:`PIL.Image`
    :param color: RGB color to convert the picto
    :type color: tuple
    :param bg_color: RGB color to use for the picto's background
    :type bg_color: tuple
    """
    if not bg_color:
        bg_color = (abs(color[0] - 255), abs(color[1] - 255), abs(color[2] - 255))
    _, _, _, alpha = pil_image.split()
    gray_pil_image = pil_image.convert('L')
    new_pil_image = ImageOps.colorize(gray_pil_image, black=bg_color, white=color)
    new_pil_image.putalpha(alpha)
    return new_pil_image


def get_pygame_main_color(surface):
    """Return the main color of the given pygame surface.
    """
    monopixel_surface = pygame.transform.scale(surface, (1, 1))
    return tuple(monopixel_surface.get_at((0, 0)))


def get_pygame_image(name, size=None, antialiasing=True, hflip=False, vflip=False,
                     crop=False, angle=0, color=(255, 255, 255), bg_color=None):
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
    :param color: recolorize the image with this RGB color
    :type color: tuple
    :param bg_color: recolorize the image background with this RGB color
    :type bg_color: tuple

    :return: pygame.Surface with image
    :rtype: object
    """
    path = get_filename(name)
    if not size and not color:
        image = pygame.image.load(path).convert()
    else:
        if osp.isfile(path):
            pil_image = Image.open(path)
        else:
            pil_image = Image.new('RGBA', size, (0, 0, 0, 0))

        if color:
            pil_image = colorize_pil_image(pil_image, color, bg_color)

        if crop:
            pil_image = pil_image.crop(sizing.new_size_by_croping_ratio(pil_image.size, size))
        pil_image = pil_image.resize(sizing.new_size_keep_aspect_ratio(pil_image.size, size),
                                     Image.ANTIALIAS if antialiasing else Image.NEAREST)

        image = pygame.image.frombuffer(pil_image.tobytes(), pil_image.size, pil_image.mode)

    if hflip or vflip:
        image = pygame.transform.flip(image, hflip, vflip)
    if angle != 0:
        image = pygame.transform.rotate(image, angle)
    return image


def get_pygame_layout_image(text_color, bg_color, layout_number, size):
    """Generate the layout image with the corresponding text.

    :param text_color: RGB color for texts
    :type text_color: tuple
    :param layout_number: number of captures on the layout
    :type layout_number: int
    :param size: maximum size of the layout surface
    :type size: tuple

    :return: surface
    :rtype: :py:class:`pygame.Surface`
    """
    layout_image = get_pygame_image("layout{0}.png".format(layout_number),
                                    size, color=text_color, bg_color=bg_color)
    text = language.get_translated_text(str(layout_number))
    if text:
        rect = layout_image.get_rect()
        rect = pygame.Rect(rect.x + rect.width * 0.3 / 2,
                           rect.y + rect.height * 0.76,
                           rect.width * 0.7, rect.height * 0.20)
        text_font = fonts.get_pygame_font(text, fonts.CURRENT, rect.width, rect.height)
        surface = text_font.render(text, True, bg_color)
        layout_image.blit(surface, surface.get_rect(center=rect.center))
    return layout_image


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


def get_picture_factory(captures, orientation=AUTO, paper_format=(4, 6), force_pil=False, dpi=600):
    """Return the picture factory use to concatenate the captures.

    :param captures: list of captures to concatenate
    :type captures: list
    :param orientation: paper orientation
    :type orientation: str
    :param paper_format: paper size in inches
    :type paper_format: tuple
    :param force_pil: force use PIL implementation
    :type force_pil: bool
    :param dpi: dot-per-inche resolution
    :type dpi: int
    """
    assert orientation in (AUTO, PORTRAIT, LANDSCAPE), "Unknown orientation '{}'".format(orientation)
    if orientation == AUTO:
        orientation = get_best_orientation(captures)

    # Ensure paper format is given in portrait (don't manage orientation with it)
    if paper_format[0] > paper_format[1]:
        paper_format = (paper_format[1], paper_format[0])

    size = (paper_format[0] * dpi, paper_format[1] * dpi)
    if orientation == LANDSCAPE:
        size = (size[1], size[0])

    if not factory.cv2 or force_pil:
        return factory.PilPictureFactory(size[0], size[1], *captures)

    return factory.OpenCvPictureFactory(size[0], size[1], *captures)
