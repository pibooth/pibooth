# -*- coding: utf-8 -*-

from PIL import Image, ImageDraw, ImageFont
from pibooth import fonts
from pibooth.pictures import sizing


def new_image_with_background(width, height, background):
    """Create a new image with the given background. The background can be
    a RGB color tuple ora PIL image.
    """
    if isinstance(background, (tuple, list)):
        return Image.new('RGB', (width, height), color=background)
    else:
        image = Image.new('RGB', (width, height))
        image.paste(background.resize(sizing.new_size_keep_aspect_ratio(background.size, image.size, 'outer')))
        return image


def concatenate_pictures_portrait(pictures, footer_texts, bg_color, text_color):
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

    matrix = matrix.resize(sizing.new_size_keep_aspect_ratio(matrix.size, (2400, 3000)), Image.ANTIALIAS)
    final_width, final_height = 2400, 3600
    footer_size = 600

    final_image = new_image_with_background(final_width, final_height, bg_color)
    final_image.paste(matrix, ((final_width - matrix.size[0]) // 2, (final_height - footer_size - matrix.size[1]) // 2), mask=matrix)

    # Text part
    draw = ImageDraw.Draw(final_image)

    # Footer 1
    name_font = ImageFont.truetype(fonts.get_filename("Amatic-Bold.ttf"), int(2 / 3. * footer_size))
    name_width, name_height = draw.textsize(footer_texts[0], font=name_font)
    footer_x = (final_width - name_width) // 2
    footer_y = final_height - footer_size - 100
    draw.text((footer_x, footer_y), footer_texts[0], text_color, font=name_font)

    # Footer 2
    date_font = ImageFont.truetype(fonts.get_filename("AmaticSC-Regular.ttf"), int(1 / 3. * footer_size))
    date_width, date_height = draw.textsize(footer_texts[1], font=date_font)
    footer_x = (final_width - date_width) // 2
    footer_y = final_height - footer_size + 300
    draw.text((footer_x, footer_y), footer_texts[1], text_color, font=date_font)

    return final_image


def concatenate_pictures_landscape(pictures, footer_texts, bg_color, text_color):
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

    matrix = matrix.resize(sizing.new_size_keep_aspect_ratio(matrix.size, (3600, 2100)), Image.ANTIALIAS)
    final_width, final_height = 3600, 2400
    footer_size = 300

    final_image = new_image_with_background(final_width, final_height, bg_color)
    final_image.paste(matrix, ((final_width - matrix.size[0]) // 2, (final_height - footer_size - matrix.size[1]) // 2), mask=matrix)

    # Text part
    draw = ImageDraw.Draw(final_image)

    # Footer 1
    name_font = ImageFont.truetype(fonts.get_filename("Amatic-Bold.ttf"), int(2 / 3. * footer_size))
    name_width, name_height = draw.textsize(footer_texts[0], font=name_font)
    footer_x = final_width // 4 - name_width // 2
    footer_y = final_height - (footer_size + name_height) // 2 - 50
    draw.text((footer_x, footer_y), footer_texts[0], text_color, font=name_font)

    # Footer 2
    date_font = ImageFont.truetype(fonts.get_filename("AmaticSC-Regular.ttf"), int(1 / 3. * footer_size))
    date_width, date_height = draw.textsize(footer_texts[1], font=date_font)
    footer_x = 3 * final_width // 4 - date_width // 2
    footer_y = final_height - (footer_size + date_height) // 2 - 50
    draw.text((footer_x, footer_y), footer_texts[1], text_color, font=date_font)

    return final_image


def concatenate_pictures(pictures, footer_texts, bg_color, text_color, orientation="auto"):
    """
    Merge up to 4 PIL images and retrun concatenated image as a new PIL image object.
    Configuration of the final picture depends on the number of given pictures.
    """
    if orientation == "auto":
        # Use the size of the first picture to determine the orientation
        if pictures[0].size[0] > pictures[0].size[1]:
            orientation = "landscape"
        else:
            orientation = "portrait"

    if orientation == "portrait":
        return concatenate_pictures_portrait(pictures, footer_texts, bg_color, text_color)
    elif orientation == "landscape":
        return concatenate_pictures_landscape(pictures, footer_texts, bg_color, text_color)
    else:
        raise ValueError("Invalid orientation '{}'".format(orientation))
