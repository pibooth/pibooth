# -*- coding: utf-8 -*-

from PIL import Image, ImageDraw, ImageFont
from pibooth import fonts
from pibooth.utils import timeit
from pibooth.pictures import sizing
try:
    import cv2
except ImportError:
    cv2 = None  # opencv is optional
import numpy as np


def new_image_with_background(width, height, background):
    """Create a new image with the given background. The background can be
    a RGB color tuple or a PIL image.
    """
    if isinstance(background, (tuple, list)):
        return Image.new('RGB', (width, height), color=background)
    else:
        image = Image.new('RGB', (width, height))
        image.paste(background.resize(sizing.new_size_keep_aspect_ratio(background.size, image.size, 'outer')))
        return image


def new_image_with_background_opencv(width, height, background):
    """Create a new image with the given background. The background can be
    a RGB color tuple or an opencv image.
    """
    if isinstance(background, (tuple, list)):
        # Small optimization for all white or all black (or all grey...) background
        if background[0] == background[1] and background[1] == background[2]:
            img = np.full((height, width, 3), background[0], np.uint8)
        else:
            img = np.zeros((height, width, 3), np.uint8)
            img[:] = (background[0], background[1], background[2])
    else:
        background = np.array(background.convert('RGB'))  # Convert from PIL image to numpy array
        img = image_resize_keep_aspect_ratio_opencv(background, width, height)

    return img


def image_resize_keep_aspect_ratio_opencv(image, width, height, inter=None):
    """Resize an image to fixed dimensions while keeping its aspect ratio. The
    image will be cropped to fit in the target dimensions.
    """
    if not inter:
        inter = cv2.INTER_AREA
    (h, w) = image.shape[:2]

    source_aspect_ratio = w / h
    target_aspect_ratio = width / height

    if source_aspect_ratio <= target_aspect_ratio:
        h_cropped = int(w / target_aspect_ratio)
        y_offset = int((h - h_cropped) / 2)
        cropped = image[y_offset:(y_offset + h_cropped), 0:w]
    else:
        w_cropped = int(h * target_aspect_ratio)
        x_offset = int((w - w_cropped) / 2)
        cropped = image[0:h, x_offset:(x_offset + w_cropped)]

    return cv2.resize(cropped, (width, height), inter)


def image_resize(image, width=None, height=None, inter=None):
    """Resize image to a specific width or height, preserving aspect ratio
    by scaling the other dimension accordingly.
    """
    if not inter:
        inter = cv2.INTER_AREA
    (h, w) = image.shape[:2]

    if width is None and height is None:
        return image

    if width is None:
        r = height / float(h)
        dim = (int(w * r), height)
    else:
        r = width / float(w)
        dim = (width, int(h * r))

    return cv2.resize(image, dim, interpolation=inter)


def get_pics_layout_size(pictures, portrait, inter_width):
    """Return picture matrix dimensions based on input pictures and margin
    between pictures.
    """
    widths, heights = zip(*(i.size for i in pictures))

    # starting here we consider that all the images have the same height and widths
    if inter_width is None:
        inter_width = max(heights) // 20

    if len(pictures) == 1:
        new_width = max(widths) + inter_width * 2
        new_height = max(heights) + inter_width * 2
    elif len(pictures) == 2:
        new_width = max(widths) + inter_width * 2 if portrait else max(widths) * 2 + inter_width * 3
        new_height = max(heights) * 2 + inter_width * 3 if portrait else max(heights) + inter_width * 2
    elif len(pictures) == 3:
        new_width = max(widths) + inter_width * 2 if portrait else max(widths) * 3 + inter_width * 4
        new_height = max(heights) * 3 + inter_width * 4 if portrait else max(heights) + inter_width * 2
    elif len(pictures) == 4:
        new_width = max(widths) * 2 + inter_width * 3
        new_height = max(heights) * 2 + inter_width * 3
    else:
        raise ValueError("List of max 4 pictures expected, got {}".format(len(pictures)))

    return new_width, new_height, inter_width


def get_pics_layout_offset(pictures, portrait, inter_width):
    """ Yield offset coordinates for up to 4 PIL images in portrait orientation...

      +---------+     +---------+     +---+-+---+     +---------+
      |         |     |   +-+   |     |   |1|   |     | +-+ +-+ |
      |         |     |   |1|   |     |   +-+   |     | |1| |2| |
      |   +-+   |     |   +-+   |     |   +-+   |     | +-+ +-+ |
      |   |1|   |     |         |     |   |2|   |     |         |
      |   +-+   |     |   +-+   |     |   +-+   |     | +-+ +-+ |
      |         |     |   |2|   |     |   +-+   |     | |3| |4| |
      |         |     |   +-+   |     |   |3|   |     | +-+ +-+ |
      +---------+     +---------+     +---+-+---+     +---------+

    ...or landscape orientation

      +-------------+     +-------------+     +-------------+     +---+-+-+-+---+
      |     +-+     |     |   +-+  +-+  |     | +-+ +-+ +-+ |     |   |1| |2|   |
      |     |1|     |     |   |1|  |2|  |     | |1| |2| |3| |     |   +-+ +-+   |
      |     +-+     |     |   +-+  +-+  |     | +-+ +-+ +-+ |     |   +-+ +-+   |
      |             |     |             |     |             |     |   |3| |4|   |
      +-------------+     +-------------+     +-------------+     +---+-+-+-+---+
    """
    x_offset = inter_width
    y_offset = inter_width

    yield x_offset, y_offset

    if 2 <= len(pictures) < 4:
        if portrait:
            y_offset += (pictures[0].size[1] + inter_width)
        else:
            x_offset += (pictures[0].size[0] + inter_width)
        yield x_offset, y_offset

    if 3 <= len(pictures) < 4:
        if portrait:
            y_offset += (pictures[1].size[1] + inter_width)
        else:
            x_offset += (pictures[1].size[0] + inter_width)
        yield x_offset, y_offset

    if len(pictures) == 4:
        x_offset += (pictures[0].size[0] + inter_width)
        yield x_offset, y_offset
        y_offset += (pictures[1].size[1] + inter_width)
        x_offset = inter_width
        yield x_offset, y_offset
        x_offset += (pictures[2].size[0] + inter_width)
        yield x_offset, y_offset


def get_final_image_dimensions(portrait, footer_texts):
    """ Return final image dimensions based on text in footers.
    """
    if portrait:
        final_width, final_height = 2400, 3600
    else:
        final_width, final_height = 3600, 2400

    if not footer_texts[0] and not footer_texts[1]:
        matrix_width, matrix_height = final_width, final_height
        footer_size = 0
    else:
        footer_size = 600 if portrait else 300
        matrix_width, matrix_height = final_width, final_height - footer_size

    return final_width, final_height, matrix_width, matrix_height, footer_size


def concatenate_pictures_PIL(portrait, pictures, footer_texts, bg_color, text_color, footer_fonts, inter_width=None):
    """ Merge up to 4 PIL images.
    """
    with timeit("Create final image with PIL"):
        new_width, new_height, inter_width = get_pics_layout_size(pictures, portrait, inter_width)
        matrix = Image.new('RGBA', (new_width, new_height))

        # Consider that the photo are correctly ordered
        offset_generator = get_pics_layout_offset(pictures, portrait, inter_width)
        for i in range(len(pictures)):
            matrix.paste(pictures[i], next(offset_generator))

        final_width, final_height, matrix_width, matrix_height, footer_size = get_final_image_dimensions(
            portrait, footer_texts)

        matrix = matrix.resize(sizing.new_size_keep_aspect_ratio(
            matrix.size, (matrix_width, matrix_height)), Image.ANTIALIAS)

        final_image = new_image_with_background(final_width, final_height, bg_color)
        final_image.paste(matrix, ((final_width - matrix.size[0]) // 2,
                                   (final_height - footer_size - matrix.size[1]) // 2), mask=matrix)

        if footer_size:
            draw_footer_text(final_image, portrait, footer_texts, footer_fonts, footer_size, text_color)

    return final_image


def concatenate_pictures_opencv(portrait, pictures, footer_texts, bg_color, text_color, footer_fonts, inter_width=None):
    """ Merge up to 4 PIL images using opencv to manipulate the images.
    """
    with timeit("Create final image with opencv"):
        matrix_raw_width, matrix_raw_height, inter_width = get_pics_layout_size(pictures, portrait, inter_width)
        final_width, final_height, matrix_width, matrix_height, footer_size = get_final_image_dimensions(
            portrait, footer_texts)
        offset_generator = get_pics_layout_offset(pictures, portrait, inter_width)

        with timeit("Init final image with background"):
            pics_scaling_factor = min(matrix_width / matrix_raw_width, matrix_height / matrix_raw_height)
            pics_x_offset = int(matrix_width - matrix_raw_width * pics_scaling_factor) // 2
            pics_y_offset = int(matrix_height - matrix_raw_height * pics_scaling_factor) // 2

            final_image = new_image_with_background_opencv(final_width, final_height, bg_color)

        with timeit("Layout pictures matrix"):
            # Consider that the photo are correctly ordered
            for i in range(len(pictures)):
                cv_pic = np.array(pictures[i].convert('RGB'))
                cv_pic = cv2.resize(cv_pic, None, fx=pics_scaling_factor,
                                    fy=pics_scaling_factor, interpolation=cv2.INTER_AREA)
                (h, w) = cv_pic.shape[:2]
                x_offset, y_offset = next(offset_generator)
                x_offset, y_offset = pics_x_offset + \
                    int(pics_scaling_factor * x_offset), pics_y_offset + int(pics_scaling_factor * y_offset)
                final_image[y_offset:(y_offset + h), x_offset:(x_offset + w)] = cv_pic
                # cv2.imshow("final_image", final_image); cv2.waitKey(); cv2.destroyAllWindows()

        with timeit("Convert final image from opencv to PIL image"):
            final_image = Image.fromarray(final_image)

        with timeit("Write text on final image"):
            if footer_size:
                draw_footer_text(final_image, portrait, footer_texts, footer_fonts, footer_size, text_color)

    return final_image


def draw_footer_text(final_image, portrait, footer_texts, footer_fonts, footer_size, text_color):
    """Draw footer text on final image.
    """
    final_width, final_height = final_image.size
    draw = ImageDraw.Draw(final_image)

    # Footer 1
    name_font = ImageFont.truetype(fonts.get_filename(footer_fonts[0]), int(2 / 3. * footer_size))
    name_width, name_height = draw.textsize(footer_texts[0], font=name_font)
    footer_x = (final_width - name_width) // 2 if portrait else final_width // 4 - name_width // 2
    footer_y = final_height - footer_size - 100 if portrait else final_height - (footer_size + name_height) // 2 - 50
    draw.text((footer_x, footer_y), footer_texts[0], text_color, font=name_font)

    # Footer 2
    date_font = ImageFont.truetype(fonts.get_filename(footer_fonts[-1]), int(1 / 3. * footer_size))
    date_width, date_height = draw.textsize(footer_texts[1], font=date_font)
    footer_x = (final_width - date_width) // 2 if portrait else 3 * final_width // 4 - date_width // 2
    footer_y = final_height - footer_size + 300 if portrait else final_height - (footer_size + date_height) // 2 - 50
    draw.text((footer_x, footer_y), footer_texts[1], text_color, font=date_font)


def concatenate_pictures(pictures, footer_texts=('', ''), footer_fonts=("Amatic-Bold", "AmaticSC-Regular"),
                         bg_color=(255, 255, 255), text_color=(0, 0, 0), orientation="auto",
                         inter_width=None):
    """ Merge up to 4 PIL images and return concatenated image as a new PIL image object.
    Configuration of the final picture depends on the number of given pictures.
    """
    if orientation == "auto":
        # Use the size of the first picture to determine the orientation
        is_portrait = pictures[0].size[0] < pictures[0].size[1]
        if len(pictures) == 1 or len(pictures) == 4:
            if is_portrait:
                orientation = "portrait"
            else:
                orientation = "landscape"
        elif len(pictures) == 2 or len(pictures) == 3:
            if is_portrait:
                orientation = "landscape"
            else:
                orientation = "portrait"
        else:
            raise ValueError("List of max 4 pictures expected, got {}".format(len(pictures)))

    if orientation == "portrait":
        if not cv2:
            return concatenate_pictures_PIL(True, pictures, footer_texts, bg_color, text_color, footer_fonts, inter_width)
        else:
            return concatenate_pictures_opencv(True, pictures, footer_texts, bg_color, text_color, footer_fonts, inter_width)
    elif orientation == "landscape":
        if not cv2:
            return concatenate_pictures_PIL(False, pictures, footer_texts, bg_color, text_color, footer_fonts, inter_width)
        else:
            return concatenate_pictures_opencv(False, pictures, footer_texts, bg_color, text_color, footer_fonts, inter_width)
    else:
        raise ValueError("Invalid orientation '{}'".format(orientation))
