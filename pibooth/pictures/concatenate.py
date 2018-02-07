# -*- coding: utf-8 -*-

from PIL import Image, ImageDraw, ImageFont
from pibooth import fonts
from pibooth.pictures import resize_keep_aspect_ratio


def concatenate_pictures(pictures, footer_texts, bg_color, text_color):
    """
    Merge up to 4 PIL images and retrun concatenated image as a new PIL image object.
    Configuration of the final picture depends on the number of given pictues::

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

    matrix = Image.new('RGB', (new_width, new_height), color=bg_color)

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

    matrix = matrix.resize(resize_keep_aspect_ratio(matrix.size, (2400, 3000)), Image.ANTIALIAS)

    final_width, final_height = 2400, 3600
    final_image = Image.new('RGB', (final_width, final_height), color=bg_color)
    final_image.paste(matrix, ((final_width - matrix.size[0]) // 2, (3000 - matrix.size[1]) // 2))

    # Text part
    x_offset = 300
    y_offset = 2900
    draw = ImageDraw.Draw(final_image)

    name_font = ImageFont.truetype(fonts.get_filename("Amatic-Bold.ttf"), 400)
    name_width, _ = draw.textsize(footer_texts[0], font=name_font)
    draw.text(((final_width - name_width) // 2, y_offset), footer_texts[0], text_color, font=name_font)

    date_font = ImageFont.truetype(fonts.get_filename("AmaticSC-Regular.ttf"), 200)
    date_width, _ = draw.textsize(footer_texts[1], font=date_font)
    draw.text(((final_width - date_width) // 2, y_offset + 400), footer_texts[1], text_color, font=date_font)

    return final_image


def generate_picture_from_files(image_files_list, footer_texts, bg_color=(255, 255, 255), text_color=(0, 0, 0)):
    """
    Generate a picture by concatenating the images in the image_files_list
    """
    list_pil_images = [Image.open(img) for img in image_files_list]

    return concatenate_pictures(list_pil_images, footer_texts, bg_color=bg_color, text_color=text_color)
