# -*- coding: utf-8 -*-

from PIL import Image, ImageDraw, ImageFont
from pibooth import fonts
from pibooth.pictures import resize_keep_aspect_ratio


def concatenate_pictures(images, footer_texts, bg_color, text_color):
    """
    Appends 4 PIL images in photobooth mode and retrun concatenated image as a new PIL image object.
    """
    widths, heights = zip(*(i.size for i in images))

    # starting here we consider that all the images have the same height and widths
    inter_width = max(heights) // 20

    # consider that we have 4 images
    new_width = max(widths) * 2 + inter_width * 3
    new_height = max(heights) * 2 + inter_width * 3

    matrix = Image.new('RGB', (new_width, new_height), color=bg_color)

    x_offset = inter_width
    y_offset = inter_width

    # Consider that the photo are correctly ordered
    matrix.paste(images[0], (x_offset, y_offset))
    x_offset = x_offset + images[0].size[0] + inter_width
    matrix.paste(images[1], (x_offset, y_offset))
    y_offset = y_offset + images[1].size[1] + inter_width
    x_offset = inter_width
    matrix.paste(images[2], (x_offset, y_offset))
    x_offset = x_offset + images[2].size[0] + inter_width
    matrix.paste(images[3], (x_offset, y_offset))

    matrix = matrix.resize(resize_keep_aspect_ratio(matrix.size, (2400, 3000)), Image.ANTIALIAS)

    final_image = Image.new('RGB', (2400, 3600), color=bg_color)
    final_image.paste(matrix, ((2400 - matrix.size[0]) // 2, (3000 - matrix.size[1]) // 2))

    # Text part
    x_offset = 600
    y_offset = 3100
    draw = ImageDraw.Draw(final_image)

    name_font = ImageFont.truetype(fonts.get_filename("Roboto-BoldItalic.ttf"), 200)
    date_font = ImageFont.truetype(fonts.get_filename("Roboto-LightItalic.ttf"), 100)

    draw.text((x_offset, y_offset), footer_texts[0], text_color, font=name_font)
    draw.text((x_offset, y_offset + 200), footer_texts[1], text_color, font=date_font)

    return final_image


def generate_picture_from_files(image_files_list, footer_texts, bg_color=(255, 255, 255), text_color=(0, 0, 0)):
    """
    Generate a picture by concatenating the images in the image_files_list
    """
    list_pil_images = [Image.open(img) for img in image_files_list]

    return concatenate_pictures(list_pil_images, footer_texts, bg_color=bg_color, text_color=text_color)
