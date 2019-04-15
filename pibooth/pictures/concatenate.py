# -*- coding: utf-8 -*-

from PIL import Image, ImageDraw, ImageFont
from pibooth import fonts
from pibooth.pictures import sizing


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


def concatenate_pictures_portrait(pictures, footer_texts, bg_color, text_color, footer_fonts, inter_width=None):
    """
    Merge up to 4 PIL images in portrait orientation.

      +---------+     +---------+     +---+-+---+     +---------+
      |         |     |   +-+   |     |   |1|   |     | +-+ +-+ |
      |         |     |   |1|   |     |   +-+   |     | |1| |2| |
      |   +-+   |     |   +-+   |     |   +-+   |     | +-+ +-+ |
      |   |1|   |     |         |     |   |2|   |     |         |
      |   +-+   |     |   +-+   |     |   +-+   |     | +-+ +-+ |
      |         |     |   |2|   |     |   +-+   |     | |3| |4| |
      |         |     |   +-+   |     |   |3|   |     | +-+ +-+ |
      +---------+     +---------+     +---+-+---+     +---------+
    """
    widths, heights = zip(*(i.size for i in pictures))

    # starting here we consider that all the images have the same height and widths
    if inter_width is None:
        inter_width = max(heights) // 20

    if len(pictures) == 1:
        new_width = max(widths) + inter_width * 2
        new_height = max(heights) + inter_width * 2
    elif len(pictures) == 2:
        new_width = max(widths) + inter_width * 2
        new_height = max(heights) * 2 + inter_width * 3
    elif len(pictures) == 3:
        new_width = max(widths) + inter_width * 2
        new_height = max(heights) * 3 + inter_width * 4
    elif len(pictures) == 4:
        new_width = max(widths) * 2 + inter_width * 3
        new_height = max(heights) * 2 + inter_width * 3
    else:
        raise ValueError("List of max 4 pictures expected, got {}".format(len(pictures)))

    matrix = Image.new('RGBA', (new_width, new_height))

    x_offset = inter_width
    y_offset = inter_width

    # Consider that the photo are correctly ordered
    matrix.paste(pictures[0], (x_offset, y_offset))
    if len(pictures) == 2:
        y_offset += (pictures[0].size[1] + inter_width)
        matrix.paste(pictures[1], (x_offset, y_offset))
    elif len(pictures) == 3:
        y_offset += (pictures[0].size[1] + inter_width)
        matrix.paste(pictures[1], (x_offset, y_offset))
        y_offset += (pictures[1].size[1] + inter_width)
        matrix.paste(pictures[2], (x_offset, y_offset))
    elif len(pictures) == 4:
        x_offset += (pictures[0].size[0] + inter_width)
        matrix.paste(pictures[1], (x_offset, y_offset))
        y_offset += (pictures[1].size[1] + inter_width)
        x_offset = inter_width
        matrix.paste(pictures[2], (x_offset, y_offset))
        x_offset += (pictures[2].size[0] + inter_width)
        matrix.paste(pictures[3], (x_offset, y_offset))

    final_width, final_height = 2400, 3600
    if not footer_texts[0] and not footer_texts[1]:
        matrix_width, matrix_height = final_width, final_height
        footer_size = 0
    else:
        matrix_width, matrix_height = 2400, 3000
        footer_size = 600

    matrix = matrix.resize(sizing.new_size_keep_aspect_ratio(
        matrix.size, (matrix_width, matrix_height)), Image.ANTIALIAS)
    final_image = new_image_with_background(final_width, final_height, bg_color)
    final_image.paste(matrix, ((final_width - matrix.size[0]) // 2,
                               (final_height - footer_size - matrix.size[1]) // 2), mask=matrix)

    if footer_size:
        draw_footer_text(final_image, footer_texts, footer_fonts, footer_size, text_color)

    return final_image


def concatenate_pictures_landscape(pictures, footer_texts, bg_color, text_color, footer_fonts, inter_width=None):
    """
    Merge up to 4 PIL images in landscape orientation.

      +-------------+     +-------------+     +-------------+     +---+-+-+-+---+
      |     +-+     |     |   +-+  +-+  |     | +-+ +-+ +-+ |     |   |1| |2|   |
      |     |1|     |     |   |1|  |2|  |     | |1| |2| |3| |     |   +-+ +-+   |
      |     +-+     |     |   +-+  +-+  |     | +-+ +-+ +-+ |     |   +-+ +-+   |
      |             |     |             |     |             |     |   |3| |4|   |
      +-------------+     +-------------+     +-------------+     +---+-+-+-+---+
    """
    widths, heights = zip(*(i.size for i in pictures))

    # starting here we consider that all the images have the same height and widths
    if inter_width is None:
        inter_width = max(heights) // 20

    if len(pictures) == 1:
        new_width = max(widths) + inter_width * 2
        new_height = max(heights) + inter_width * 2
    elif len(pictures) == 2:
        new_width = max(widths) * 2 + inter_width * 3
        new_height = max(heights) + inter_width * 2
    elif len(pictures) == 3:
        new_width = max(widths) * 3 + inter_width * 4
        new_height = max(heights) + inter_width * 2
    elif len(pictures) == 4:
        new_width = max(widths) * 2 + inter_width * 3
        new_height = max(heights) * 2 + inter_width * 3
    else:
        raise ValueError("List of max 4 pictures expected, got {}".format(len(pictures)))

    matrix = Image.new('RGBA', (new_width, new_height))

    x_offset = inter_width
    y_offset = inter_width

    # Consider that the photo are correctly ordered
    matrix.paste(pictures[0], (x_offset, y_offset))
    if len(pictures) == 2:
        x_offset += (pictures[0].size[0] + inter_width)
        matrix.paste(pictures[1], (x_offset, y_offset))
    elif len(pictures) == 3:
        x_offset += (pictures[0].size[0] + inter_width)
        matrix.paste(pictures[1], (x_offset, y_offset))
        x_offset += (pictures[1].size[0] + inter_width)
        matrix.paste(pictures[2], (x_offset, y_offset))
    elif len(pictures) == 4:
        x_offset += (pictures[0].size[0] + inter_width)
        matrix.paste(pictures[1], (x_offset, y_offset))
        y_offset += (pictures[1].size[1] + inter_width)
        x_offset = inter_width
        matrix.paste(pictures[2], (x_offset, y_offset))
        x_offset += (pictures[2].size[0] + inter_width)
        matrix.paste(pictures[3], (x_offset, y_offset))

    final_width, final_height = 3600, 2400
    if not footer_texts[0] and not footer_texts[1]:
        matrix_width, matrix_height = final_width, final_height
        footer_size = 0
    else:
        matrix_width, matrix_height = 3600, 2100
        footer_size = 300

    matrix = matrix.resize(sizing.new_size_keep_aspect_ratio(
        matrix.size, (matrix_width, matrix_height)), Image.ANTIALIAS)
    final_image = new_image_with_background(final_width, final_height, bg_color)
    final_image.paste(matrix, ((final_width - matrix.size[0]) // 2,
                               (final_height - footer_size - matrix.size[1]) // 2), mask=matrix)

    if footer_size:
        draw_footer_text(final_image, footer_texts, footer_fonts, footer_size, text_color)

    return final_image


def draw_footer_text(final_image, footer_texts, footer_fonts, footer_size, text_color):
    final_width, final_height = final_image.size
    draw = ImageDraw.Draw(final_image)

    # Footer 1
    name_font = ImageFont.truetype(footer_fonts[0], int(2 / 3. * footer_size))
    name_width, name_height = draw.textsize(footer_texts[0], font=name_font)
    footer_x = final_width // 4 - name_width // 2
    footer_y = final_height - (footer_size + name_height) // 2 - 50
    draw.text((footer_x, footer_y), footer_texts[0], text_color, font=name_font)

    # Footer 2
    date_font = ImageFont.truetype(footer_fonts[-1], int(1 / 3. * footer_size))
    date_width, date_height = draw.textsize(footer_texts[1], font=date_font)
    footer_x = 3 * final_width // 4 - date_width // 2
    footer_y = final_height - (footer_size + date_height) // 2 - 50
    draw.text((footer_x, footer_y), footer_texts[1], text_color, font=date_font)


def concatenate_pictures(pictures, footer_texts=('', ''), bg_color=(255, 255, 255), text_color=(0, 0, 0), orientation="auto", footer_fonts='none', inter_width=None):
    """
    Merge up to 4 PIL images and return concatenated image as a new PIL image object.
    Configuration of the final picture depends on the number of given pictures.
    """
    if footer_fonts == 'none':
        footer_fonts = [fonts.get_filename("Amatic-Bold.ttf"), fonts.get_filename("AmaticSC-Regular.ttf")]
    else:
        footer_fonts = footer_fonts.split(',')

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
        return concatenate_pictures_portrait(pictures, footer_texts, bg_color, text_color, footer_fonts, inter_width)
    elif orientation == "landscape":
        return concatenate_pictures_landscape(pictures, footer_texts, bg_color, text_color, footer_fonts, inter_width)
    else:
        raise ValueError("Invalid orientation '{}'".format(orientation))
