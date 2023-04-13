# -*- coding: utf-8 -*-

"""Module gathering PIL and Pygame images hepers.
"""


import os.path as osp
from PIL import ImageOps
import pygame
from pibooth import language
from pibooth import fonts
from pibooth.pictures import factory
from pibooth.pictures import sizing


AUTO = 'auto'
PORTRAIT = 'portrait'
LANDSCAPE = 'landscape'

ALIGN_TOP_LEFT = 'top-left'
ALIGN_TOP_CENTER = 'top-center'
ALIGN_TOP_RIGHT = 'top-right'
ALIGN_CENTER_LEFT = 'center-left'
ALIGN_CENTER = 'center'
ALIGN_CENTER_RIGHT = 'center-right'
ALIGN_BOTTOM_LEFT = 'bottom-left'
ALIGN_BOTTOM_CENTER = 'bottom-center'
ALIGN_BOTTOM_RIGHT = 'bottom-right'


def get_filename(name):
    """Return absolute path to a picture located in the current package.

    :param name: name of an image located in language folders
    :type name: str

    :return: absolute image path
    :rtype: str
    """
    return osp.join(osp.dirname(osp.abspath(__file__)), 'assets', name)


def colorize_pil_image(pil_image, color, bg_color=None):
    """Create a "colorized" copy of a PIL image in white to the corresponding color.

    :param pil_image: PIL image to be colorized
    :type pil_image: :py:class:`PIL.Image`
    :param color: RGB color to convert the picto
    :type color: tuple
    :param bg_color: RGB color to use for the picto's background
    :type bg_color: tuple

    :return: new colorized Image instance
    :rtype: object
    """
    if not bg_color:
        bg_color = (abs(color[0] - 255), abs(color[1] - 255), abs(color[2] - 255))
    gray_pil_image = pil_image.convert('L')
    new_pil_image = ImageOps.colorize(gray_pil_image, black=bg_color, white=color)
    if pil_image.mode in ('RGBA', 'LA') or (pil_image.mode == 'P' and 'transparency' in pil_image.info):
        _, _, _, alpha = pil_image.split()
        new_pil_image.putalpha(alpha)
    return new_pil_image


def colorize_pygame_image(surface, color):
    """Create a "colorized" copy of a surface (replaces RGB values with the given color, preserving
    the per-pixel alphas of original).

    :param surface: surface to create a colorized copy of
    :type surface: object
    :param color: RGB color to use (original alpha values are preserved)
    :type color: tuple

    :return: new colorized Surface instance
    :rtype: object
    """
    surface = surface.copy()
    # zero out RGB values
    surface.fill((0, 0, 0, 255), None, pygame.BLEND_RGBA_MULT)
    # add in new RGB values
    surface.fill(color[0:3] + (0,), None, pygame.BLEND_RGBA_ADD)
    return surface


def load_pygame_image(filename):
    """Load Pygame image from located in `pibooth.pictures.assets` folder
    or from path.

    :param filename: name of asset (with extension) or path to an image file
    :type filename: str

    :return: Pygame surface
    :rtype: object
    """
    if osp.isfile(filename):
        path = filename
    else:
        path = get_filename(filename)

    if osp.isfile(path):
        return pygame.image.load(path).convert_alpha()
    raise ValueError(f"No such image file '{filename}'")


def transform_pygame_image(surface, size, antialiasing=True, hflip=False, vflip=False,
                           angle=0, crop=False, color=None):
    """Resize a Pygame surface, the image is resized keeping the original
    surface's aspect ratio.

    :param surface: Pygame surface to resize
    :type surface: object
    :param size: resize image to this size
    :type size: tuple
    :param antialiasing: use antialiasing algorithm when resize
    :type antialiasing: bool
    :param hflip: apply an horizontal flip
    :type hflip: bool
    :param vflip: apply a vertical flip
    :type vflip: bool
    :param crop: crop image to fit the size keeping aspect ratio
    :type crop: bool
    :param angle: angle of rotation of the image
    :type angle: int
    :param color: recolorize image
    :type color: tuple

    :return: pygame.Surface with image
    :rtype: object
    """
    if crop:
        resize_type = 'outer'
    else:
        resize_type = 'inner'

    if angle != 0:
        surface = pygame.transform.rotate(surface, angle)

    if size != surface.get_size():
        if antialiasing:
            image = pygame.transform.smoothscale(
                surface, sizing.new_size_keep_aspect_ratio(surface.get_size(), size, resize_type))
        else:
            image = pygame.transform.scale(surface, sizing.new_size_keep_aspect_ratio(
                surface.get_size(), size, resize_type))
    else:
        image = surface.copy()

    if crop and size != image.get_size():
        # Crop image to fill surface
        new_surface = pygame.Surface(size, pygame.SRCALPHA, 32)
        new_surface.blit(image, (0, 0), sizing.new_size_by_croping_ratio(image.get_rect().size, size))
        image = new_surface
    elif size != image.get_size():
        # Center image on surface
        new_surface = pygame.Surface(size, pygame.SRCALPHA, 32)
        new_surface.blit(image, image.get_rect(center=new_surface.get_rect().center))
        image = new_surface

    if hflip or vflip:
        image = pygame.transform.flip(image, hflip, vflip)
    if color:
        image = colorize_pygame_image(image, color)
    return image


def text_to_pygame_image(text, size, color, align='center', bg_color=None, font_name=None):
    """Return a surface the text fit inside.

    The ``align`` parameter can be one of:
       * top-left
       * top-center
       * top-right
       * center-left
       * center
       * center-right
       * bottom-left
       * bottom-center
       * bottom-right
    """
    lines = text.splitlines()
    surface = pygame.Surface(size, pygame.SRCALPHA, 32)

    font = fonts.get_pygame_font(max(lines, key=len), font_name or fonts.CURRENT, size[0], size[1] // len(lines))
    for i, line in enumerate(lines):
        text_surface = font.render(line, True, color)

        loc = {}

        if align.endswith('left'):
            loc['left'] = 0
        elif align.endswith('center'):
            loc['centerx'] = surface.get_rect().centerx
        elif align.endswith('right'):
            loc['right'] = surface.get_rect().right
        else:
            raise ValueError(f"Invalid horizontal alignment '{align}'")

        line_height = text_surface.get_rect().height
        if align.startswith('top'):
            loc['top'] = i * line_height
        elif align.startswith('center'):
            loc['top'] = surface.get_rect().centery - len(lines) * line_height // 2 + i * line_height
        elif align.startswith('bottom'):
            loc['bottom'] = surface.get_rect().bottom - (len(lines) - 1 - i) * line_height
        else:
            raise ValueError(f"Invalid vertical alignment '{align}'")

        if bg_color:
            bg_surface = pygame.Surface(text_surface.get_size(), pygame.SRCALPHA, 32)
            bg_surface.fill(bg_color)
            surface.blit(bg_surface, text_surface.get_rect(**loc))

        surface.blit(text_surface, text_surface.get_rect(**loc))
    return surface


def get_layout_asset(index, text_color, bg_color):
    """Return the layout image with the corresponding text.

    :param index: number of captures on the layout
    :type index: int
    :param text_color: RGB color for text
    :type text_color: tuple
    :param bg_color: RGB color for asset image
    :type bg_color: tuple

    :return: surface
    :rtype: :py:class:`pygame.Surface`
    """
    layout_image = colorize_pygame_image(
        load_pygame_image(f"layout{index}.png"), bg_color)
    text = language.get_translated_text(str(index))
    if text:
        rect = layout_image.get_rect()
        rect = pygame.Rect(rect.x + rect.width * 0.3 / 2,
                           rect.y + rect.height * 0.76,
                           rect.width * 0.7, rect.height * 0.20)
        text_font = fonts.get_pygame_font(text, fonts.CURRENT, rect.width, rect.height)
        surface = text_font.render(text, True, text_color)
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
        raise ValueError(f"List of max 4 pictures expected, got {len(captures)}")
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

    :return: PictureFactory instance
    :rtype: object
    """
    assert orientation in (AUTO, PORTRAIT, LANDSCAPE), f"Unknown orientation '{orientation}'"
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
