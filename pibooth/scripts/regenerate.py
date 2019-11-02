# -*- coding: utf-8 -*-

"""Pibooth picture regeneration module.
"""

import os
from os import path as osp

from PIL import Image

from pibooth.utils import LOGGER, configure_logging
from pibooth.config import PiConfigParser
from pibooth.pictures import get_picture_maker


def get_captures(images_folder):
    """Get a list of images from the folder given in input
    """
    captures_paths = os.listdir(images_folder)
    captures = []
    for capture_path in captures_paths:
        try:
            image = Image.open(osp.join(images_folder, capture_path))
            captures.append(image)
        except OSError:
            LOGGER.info("File %s doesn't seem to be an image", capture_path)
    return captures


def regenerate_all_images(config):
    """Regenerate the pibboth images from the raw images and the config
    """
    captures_folders = config.getpath('GENERAL', 'directory')
    capture_choices = config.gettuple('PICTURE', 'captures', int)

    backgrounds = config.gettuple('PICTURE', 'backgrounds', ('color', 'path'), 2)
    overlays = config.gettuple('PICTURE', 'overlays', 'path', 2)

    texts = [config.get('PICTURE', 'footer_text1').strip('"'),
             config.get('PICTURE', 'footer_text2').strip('"')]
    colors = config.gettuple('PICTURE', 'text_colors', 'color', len(texts))
    text_fonts = config.gettuple('PICTURE', 'text_fonts', str, len(texts))
    alignments = config.gettuple('PICTURE', 'text_alignments', str, len(texts))

    # Part that fetch the captures
    for captures_folder in os.listdir(osp.join(captures_folders, 'raw')):
        captures_folder_path = osp.join(captures_folders, 'raw', captures_folder)
        if not osp.isdir(captures_folder_path):
            continue
        captures = get_captures(captures_folder_path)
        LOGGER.info("Generating image from raws in folder %s", captures_folder_path)

        if len(captures) == capture_choices[0]:
            overlay = overlays[0]
            background = backgrounds[0]
        elif len(captures) == capture_choices[1]:
            overlay = overlays[1]
            background = backgrounds[1]
        else:
            LOGGER.warning("Folder %s doesn't contain the correct number of pictures", captures_folder_path)
            continue

        maker = get_picture_maker(captures, config.get('PICTURE', 'orientation'))

        maker.set_background(background)
        if any(elem != '' for elem in texts):
            for params in zip(texts, text_fonts, colors, alignments):
                maker.add_text(*params)
        if config.getboolean('PICTURE', 'captures_cropping'):
            maker.set_cropping()
        if overlay:
            maker.set_overlay(overlay)

        picture_file = osp.join(captures_folders, captures_folder + "_pibooth.jpg")
        maker.save(picture_file)


def main():
    """Application entry point.
    """
    configure_logging()
    config = PiConfigParser("~/.config/pibooth/pibooth.cfg")
    regenerate_all_images(config)


if __name__ == "__main__":
    main()
