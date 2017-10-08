#!/usr/bin/env python3

from PIL import Image, ImageDraw, ImageFont

def generate_photo(images, footer_texts, bg_color, text_color):
    """
    Appends 4 PIL images in photobooth mode and retrun concatenated image as a new PIL image object.
    """
    widths, heights = zip(*(i.size for i in images))

    inter_width = max(heights)//20
    new_width = max(widths)*2 + inter_width*3
    new_height = max(heights)*2 + inter_width*6

    new_image = Image.new('RGB', (new_width, new_height), color=bg_color)

    x_offset = inter_width
    y_offset = inter_width

    # Consider that the photo are correctly ordered
    new_image.paste(images[0], (x_offset, y_offset))
    x_offset = x_offset + images[0].size[0] + inter_width
    new_image.paste(images[1], (x_offset, y_offset))
    y_offset = y_offset + images[1].size[1] + inter_width
    x_offset = inter_width
    new_image.paste(images[2], (x_offset, y_offset))
    x_offset = x_offset + images[2].size[0] + inter_width
    new_image.paste(images[3], (x_offset, y_offset))

    # Text part
    x_offset = 11*inter_width
    y_offset = y_offset + images[3].size[1]+ inter_width
    draw = ImageDraw.Draw(new_image)

    name_font = ImageFont.truetype("fonts/Roboto-BoldItalic.ttf", inter_width)
    date_font = ImageFont.truetype("fonts/Roboto-LightItalic.ttf", inter_width//2)

    draw.text((x_offset, y_offset), footer_texts[0], text_color, font=name_font)
    draw.text((x_offset, y_offset+inter_width), footer_texts[1], text_color, font=date_font)

    return new_image

def generate_photo_from_files(image_files_list, output_file, footer_texts, bg_color=(255, 255, 255), text_color=(0, 0, 0)):
    """
    Generate the output_file by concatenating the image in the image_files_list
    """
    list_pil_images = []
    for img in image_files_list:
        image = Image.open(img)
        if image.size[0] > image.size[1]:
            image = image.rotate(-90, expand=True)
        list_pil_images.append(image)

    # LIST_PIL_IMAGES = [Image.open(img) for img in LIST_IMAGES]
    new_image = generate_photo(list_pil_images, footer_texts,
                               bg_color=bg_color, text_color=text_color)
    new_image.save(output_file)
