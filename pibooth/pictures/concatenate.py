# -*- coding: utf-8 -*-

from PIL import Image, ImageDraw, ImageFont
from pibooth import fonts
from pibooth.pictures import sizing


def concatenate_pictures(pictures, footer_texts, bg_color, text_color, orientation="portrait"):
    """
    Merge up to 4 PIL images and retrun concatenated image as a new PIL image object.
    Configuration of the final picture depends on the number of given pictures::

    In portrait orientation

      +---------+     +---------+     +---+-+---+     +---------+
      |         |     |   +-+   |     |   |1|   |     | +-+ +-+ |
      |         |     |   |1|   |     |   +-+   |     | |1| |2| |
      |   +-+   |     |   +-+   |     |   +-+   |     | +-+ +-+ |
      |   |1|   |     |         |     |   |2|   |     |         |
      |   +-+   |     |   +-+   |     |   +-+   |     | +-+ +-+ |
      |         |     |   |2|   |     |   +-+   |     | |3| |4| |
      |         |     |   +-+   |     |   |3|   |     | +-+ +-+ |
      +---------+     +---------+     +---+-+---+     +---------+

    In landscape orientation

      +---------+     +----------+     +-------------+     +---------+
      |         |     |          |     |             |     | +-+ +-+ |
      |         |     |          |     |             |     | |1| |2| |
      |   +-+   |     | +-+  +-+ |     | +-+ +-+ +-+ |     | +-+ +-+ |
      |   |1|   |     | |1|  |2| |     | |1| |2| |3| |     |         |
      |   +-+   |     | +-+  +-+ |     | +-+ +-+ +-+ |     | +-+ +-+ |
      |         |     |          |     |             |     | |3| |4| |
      |         |     |          |     |             |     | +-+ +-+ |
      +---------+     +----------+     +-------------+     +---------+
    """
    widths, heights = zip(*(i.size for i in pictures))

    # starting here we consider that all the images have the same height and widths
    inter_width = max(heights) // 20

    if len(pictures) == 1:
        new_width = max(widths) + inter_width * 2
        new_height = max(heights) + inter_width * 2
    elif len(pictures) == 2:
        if orientation == "portrait":
            new_width = max(widths) + inter_width * 2
            new_height = max(heights) * 2 + inter_width * 3
        if orientation == "landscape":
            new_width = max(widths) * 2 + inter_width * 3
            new_height = max(heights) + inter_width * 2
    elif len(pictures) == 3:
        if orientation == "portrait":
            new_width = max(widths) + inter_width * 2
            new_height = max(heights) * 3 + inter_width * 4
        if orientation == "landscape":
            new_width = max(widths) * 3 + inter_width * 4
            new_height = max(heights) + inter_width * 2
    elif len(pictures) == 4:
        new_width = max(widths) * 2 + inter_width * 3
        new_height = max(heights) * 2 + inter_width * 3
    else:
        raise ValueError("List of max 4 pictures expected, got {}".format(len(pictures)))

    matrix = Image.new('RGB', (new_width, new_height), color=bg_color)

    x_offset = inter_width
    y_offset = inter_width

    # Consider that the photo are correctly ordered
    matrix.paste(pictures[0], (x_offset, y_offset))
    if len(pictures) == 2 and orientation == "portrait":
        y_offset += (pictures[0].size[1] + inter_width)
        matrix.paste(pictures[1], (x_offset, y_offset))
    if len(pictures) == 2 and orientation == "landscape":
        x_offset += (pictures[0].size[0] + inter_width)
        matrix.paste(pictures[1], (x_offset, y_offset))
    elif len(pictures) == 3 and orientation == "portrait":
        y_offset += (pictures[0].size[1] + inter_width)
        matrix.paste(pictures[1], (x_offset, y_offset))
        y_offset += (pictures[1].size[1] + inter_width)
        matrix.paste(pictures[2], (x_offset, y_offset))
    elif len(pictures) == 3 and orientation == "landscape":
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

    if orientation == "portrait":
        matrix = matrix.resize(sizing.new_size_keep_aspect_ratio(matrix.size, (2400, 3000)), Image.ANTIALIAS)
        final_width, final_height = 2400, 3600
        footer_size = 600
    else:
        matrix = matrix.resize(sizing.new_size_keep_aspect_ratio(matrix.size, (3600, 2100)), Image.ANTIALIAS)
        final_width, final_height = 3600, 2400
        footer_size = 300

    final_image = Image.new('RGB', (final_width, final_height), color=bg_color)
    final_image.paste(matrix, ((final_width - matrix.size[0]) // 2, (final_height - footer_size - matrix.size[1]) // 2))

    # Text part
    draw = ImageDraw.Draw(final_image)

    # Footer 1
    name_font = ImageFont.truetype(fonts.get_filename("Amatic-Bold.ttf"), int(2 / 3 * footer_size))
    name_width, name_height = draw.textsize(footer_texts[0], font=name_font)
    if orientation == "portrait":
        footer_x = (final_width - name_width) // 2
        footer_y = final_height - footer_size - 100
    else:
        footer_x = final_width // 4 - name_width // 2
        footer_y = final_height - (footer_size + name_height) // 2 - 50
    draw.text((footer_x, footer_y), footer_texts[0], text_color, font=name_font)

    # Footer 2
    date_font = ImageFont.truetype(fonts.get_filename("AmaticSC-Regular.ttf"), int(1 / 3 * footer_size))
    date_width, date_height = draw.textsize(footer_texts[1], font=date_font)
    if orientation == "portrait":
        footer_x = (final_width - date_width) // 2
        footer_y = final_height - footer_size + 300
    else:
        footer_x = 3 * final_width // 4 - date_width // 2
        footer_y = final_height - (footer_size + date_height) // 2 - 50
    draw.text((footer_x, footer_y), footer_texts[1], text_color, font=date_font)

    return final_image
