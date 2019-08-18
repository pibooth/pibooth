# -*- coding: utf-8 -*-

import os
import os.path as osp
from pibooth import fonts
from pibooth.utils import timeit
from pibooth.pictures import sizing
from PIL import Image, ImageDraw, ImageFont

try:
    import cv2
    import numpy as np
except ImportError:
    cv2 = None


class PictureMaker(object):

    """
    Concatenate up to 4 PIL images in portrait orientation...

         +---------+           +---------+           +---+-+---+           +---------+
         |         |           |   +-+   |           |   |1|   |           | +-+ +-+ |
         |         |           |   |1|   |           |   +-+   |           | |1| |2| |
         |   +-+   |           |   +-+   |           |   +-+   |           | +-+ +-+ |
         |   |1|   |           |         |           |   |2|   |           |         |
         |   +-+   |           |   +-+   |           |   +-+   |           | +-+ +-+ |
         |         |           |   |2|   |           |   +-+   |           | |3| |4| |
         |         |           |   +-+   |           |   |3|   |           | +-+ +-+ |
         +---------+           +---------+           +---+-+---+           +---------+

    ...or landscape orientation

      +---------------+     +---------------+     +---------------+     +----+-+-+-+----+
      |      +-+      |     |    +-+  +-+   |     |  +-+ +-+ +-+  |     |    |1| |2|    |
      |      |1|      |     |    |1|  |2|   |     |  |1| |2| |3|  |     |    +-+ +-+    |
      |      +-+      |     |    +-+  +-+   |     |  +-+ +-+ +-+  |     |    +-+ +-+    |
      |               |     |               |     |               |     |    |3| |4|    |
      +---------------+     +---------------+     +---------------+     +----+-+-+-+----+
    """

    CENTER = 'center'
    RIGHT = 'right'
    LEFT = 'left'

    def __init__(self, width, height, *images):
        assert len(images) in range(1, 5), "1 to 4 images can be concatenated"
        self._texts = []
        self._texts_height = 0
        self._final = None
        self._margin = None
        self._images = images
        self._background_color = (255, 255, 255)
        self._background_image = None

        self.width = width
        self.height = height
        self.is_portrait = self.width < self.height

    def _build_background(self):
        """Create an image with the given background.

        :return: image object which depends on the child class implementation.
        :rtype: object
        """
        raise NotImplementedError

    def _build_matrix(self, image):
        """Draw the images matrix on the given image.

        :return: image object which depends on the child class implementation.
        :rtype: object
        """
        raise NotImplementedError

    def _build_final_image(self, image):
        """Create the final PIL image and set it to the _final attribute.
        """
        raise NotImplementedError

    def _build_texts(self):
        """Draw texts on a PIL image (PIL is used instead of OpenCV
        because it is able to draw any fonts without ext).
        """
        offset_generator = self._iter_texts_position()
        draw = ImageDraw.Draw(self._final)
        for text, font_name, color, align in self._texts:
            text_x, text_y, max_width, max_height = next(offset_generator)
            if not text:  # Empty string: go to next text position
                continue
            font = self._get_font(text, font_name, max_width, max_height)
            (text_width, _baseline), (offset_x, offset_y) = font.font.getsize(text)
            if align == self.CENTER:
                text_x += (max_width - text_width) // 2
            elif align == self.RIGHT:
                text_x += (max_width - text_width)
            draw.text((text_x - offset_x // 2, text_y - offset_y // 2), text, color, font=font)

    def _build_raw_matrix_layout(self, margin=None):
        """Return matrix dimensions based on input images and margin
        between images.

        `raw` because the matrix does not fit to the final size.

        :param margin: margin between images in pixel
        :type margin: int
        """
        widths, heights = zip(*(i.size for i in self._images))

        # Considering that all images have the same height and widths
        if margin is None:
            margin = max(heights) // 20

        if len(self._images) == 1:
            matrix_width = max(widths) + margin * 2
            matrix_height = max(heights) + margin * 2
        elif len(self._images) == 2:
            matrix_width = max(widths) + margin * 2 if self.is_portrait else max(widths) * 2 + margin * 3
            matrix_height = max(heights) * 2 + margin * 3 if self.is_portrait else max(heights) + margin * 2
        elif len(self._images) == 3:
            matrix_width = max(widths) + margin * 2 if self.is_portrait else max(widths) * 3 + margin * 4
            matrix_height = max(heights) * 3 + margin * 4 if self.is_portrait else max(heights) + margin * 2
        elif len(self._images) == 4:
            matrix_width = max(widths) * 2 + margin * 3
            matrix_height = max(heights) * 2 + margin * 3
        else:
            raise ValueError("List of max 4 images expected, got {}".format(len(self._images)))

        return matrix_width, matrix_height, margin

    def _get_font(self, text, font_name, max_width, max_height):
        """Create the font object which fit the given rectangle.

        :param text: text to draw
        :type text: str
        :param font_name: name or path to font definition file
        :type font_name: str
        :param max_width: width of the rect to fit
        :type max_width: int
        :param max_height: height of the rect to fit
        :type max_height: int

        :return: PIL.Font instance
        :rtype: object
        """
        start, end = 0, self._texts_height
        while start < end:
            k = (start + end) // 2
            font = ImageFont.truetype(font_name, k)
            font_size = font.getsize(text)
            if font_size[0] > max_width or font_size[1] > max_height:
                end = k
            else:
                start = k + 1
        return ImageFont.truetype(font_name, start)

    def _iter_raw_matrix_position(self, margin=None):
        """Yield offset coordinates for each image.

        `raw` because the matrix does not fit to the final size.

        :param margin: margin between images in pixel
        :type margin: int

        :return: (image_x, image_y)
        :rtype: tuple
        """
        # Considering that all images have the same height and widths
        if margin is None:
            _, heights = zip(*(i.size for i in self._images))
            margin = max(heights) // 20

        x_offset = margin
        y_offset = margin

        yield x_offset, y_offset

        if 2 <= len(self._images) < 4:
            if self.is_portrait:
                y_offset += (self._images[0].size[1] + margin)
            else:
                x_offset += (self._images[0].size[0] + margin)
            yield x_offset, y_offset

        if 3 <= len(self._images) < 4:
            if self.is_portrait:
                y_offset += (self._images[1].size[1] + margin)
            else:
                x_offset += (self._images[1].size[0] + margin)
            yield x_offset, y_offset

        if len(self._images) == 4:
            x_offset += (self._images[0].size[0] + margin)
            yield x_offset, y_offset
            y_offset += (self._images[1].size[1] + margin)
            x_offset = margin
            yield x_offset, y_offset
            x_offset += (self._images[2].size[0] + margin)
            yield x_offset, y_offset

    def _iter_texts_position(self, margin=None):
        """Yield top-left coordinates and size rectangle for each text.

        :param margin: margin between texts in pixel
        :type margin: int

        :return: (text_x, text_y, text_width, text_height)
        :rtype: tuple
        """
        if margin is None:
            margin = 20

        text_x, text_y = margin, self.height - self._texts_height

        if self.is_portrait:
            text_width = self.width - 2 * margin
            text_height = (self._texts_height - margin * (len(self._texts) + 1)) // (len(self._texts) + 1)
            for i in range(len(self._texts)):
                if i == 0:
                    text_y += margin
                    yield text_x, text_y, text_width, 2 * text_height
                elif i == 1:
                    text_y += margin + 2 * text_height
                    yield text_x, text_y, text_width, text_height
                else:
                    text_y += margin + text_height
                    yield text_x, text_y, text_width, text_height
        else:
            text_width = (self.width - margin * (len(self._texts) + 1)) // len(self._texts)
            text_height = (self._texts_height - 2 * margin) // 2
            for i in range(len(self._texts)):
                if i == 0:
                    yield text_x, text_y + margin, text_width, 2 * text_height
                else:
                    text_x += margin + text_width
                    yield text_x, text_y + (self._texts_height - text_height) // 2, text_width, text_height

    def add_text(self, text, font_name, color, align=CENTER):
        """Add a new text.
        """
        assert align in [self.CENTER, self.RIGHT, self.LEFT], "Unknown aligment '{}'".format(align)
        self._texts.append((text, fonts.get_filename(font_name), color, align))
        if self.is_portrait:
            self._texts_height = 600
        else:
            self._texts_height = 300
        self._final = None  # Force rebuild

    def set_background(self, color_or_path):
        """Set background color (RGB tuple) or path to an image that used to
        fill the background.

        :param color_or_path: RGB color tuple or image path
        :type color_or_path: tuple or str
        """
        if isinstance(color_or_path, (tuple, list)):
            assert len(color_or_path) == 3, "Length of 3 is required for RGB tuple"
            self._background_color = color_or_path
        else:
            color_or_path = osp.abspath(color_or_path)
            if not osp.isfile(color_or_path):
                raise ValueError("Invalid background image '{}'".format(color_or_path))
            self._background_image = color_or_path
        self._final = None  # Force rebuild

    def set_margin(self, margin):
        """Set margin between concatenated images.

        :param margin: margin in pixels
        :type margin: int
        """
        self._margin = margin

    def build(self, rebuild=False):
        """Build the final image or doas nothing if the final image
        has already been built previously.

        :param rebuild: force re-build image
        :type rebuild: bool

        :return: PIL.Image instance
        :rtype: object
        """
        if not self._final or rebuild:

            with timeit("{}: create background".format(self.__class__.__name__)):
                image = self._build_background()

            with timeit("{}: concatenate images".format(self.__class__.__name__)):
                image = self._build_matrix(image)

            with timeit("{}: assemble final image".format(self.__class__.__name__)):
                self._build_final_image(image)

            assert self._final is not None, "_build_final_image() have to set the _final attribute"

            with timeit("{}: draw texts".format(self.__class__.__name__)):
                self._build_texts()

        return self._final

    def save(self, path):
        """Build if not already done and save final image in a file.

        :param path: path to save
        :type path: str

        :return: PIL.Image instance
        :rtype: object
        """
        dirname = osp.dirname(osp.abspath(path))
        if not osp.isdir(dirname):
            os.mkdir(dirname)
        image = self.build()
        with timeit("Save image '{}'".format(path)):
            image.save(path)
        return image


class PilPictureMaker(PictureMaker):

    def _build_final_image(self, image):
        """See upper class description.
        """
        self._final = image

    def _build_background(self):
        """See upper class description.
        """
        if self._background_image:
            image = Image.new('RGB', (self.width, self.height))
            bg = Image.open(self._background_image)
            image.paste(bg.resize(sizing.new_size_keep_aspect_ratio(bg.size, image.size, 'outer')))
        else:
            image = Image.new('RGB', (self.width, self.height), color=self._background_color)

        return image

    def _build_matrix(self, image):
        """See upper class description.
        """
        raw_matrix_width, raw_matrix_height, margin = self._build_raw_matrix_layout(self._margin)
        matrix = Image.new('RGBA', (raw_matrix_width, raw_matrix_height))

        offset_generator = self._iter_raw_matrix_position(margin)

        for pil_image in self._images:
            matrix.paste(pil_image, next(offset_generator))

        matrix = matrix.resize(sizing.new_size_keep_aspect_ratio(
            matrix.size, (self.width, self.height - self._texts_height)), Image.ANTIALIAS)

        image.paste(matrix, ((self.width - matrix.size[0]) // 2,
                             (self.height - self._texts_height - matrix.size[1]) // 2), mask=matrix)

        return image


class OpenCvPictureMaker(PictureMaker):

    def _image_resize_keep_aspect_ratio_opencv(self, image, width, height, inter=None):
        """Resize an image to fixed dimensions while keeping its aspect ratio. The
        image will be cropped to fit in the target dimensions.
        """
        if not inter:
            inter = cv2.INTER_AREA
        h, w = image.shape[:2]

        source_aspect_ratio = float(w) / h
        target_aspect_ratio = float(width) / height

        if source_aspect_ratio <= target_aspect_ratio:
            h_cropped = int(w / target_aspect_ratio)
            y_offset = int((float(h) - h_cropped) / 2)
            cropped = image[y_offset:(y_offset + h_cropped), 0:w]
        else:
            w_cropped = int(h * target_aspect_ratio)
            x_offset = int((float(w) - w_cropped) / 2)
            cropped = image[0:h, x_offset:(x_offset + w_cropped)]

        return cv2.resize(cropped, (width, height), interpolation=inter)

    def _build_final_image(self, image):
        """See upper class description.
        """
        self._final = Image.fromarray(image)

    def _build_background(self):
        """See upper class description.
        """
        if self._background_image:
            bg = cv2.cvtColor(cv2.imread(self._background_image), cv2.COLOR_BGR2RGB)
            image = self._image_resize_keep_aspect_ratio_opencv(bg, self.width, self.height)
        else:
            # Small optimization for all white or all black (or all grey...) background
            if self._background_color[0] == self._background_color[1] and self._background_color[1] == self._background_color[2]:
                image = np.full((self.height, self.width, 3), self._background_color[0], np.uint8)
            else:
                image = np.zeros((self.height, self.width, 3), np.uint8)
                image[:] = (self._background_color[0], self._background_color[1], self._background_color[2])

        return image

    def _build_matrix(self, image):
        """See upper class description.
        """
        raw_matrix_width, raw_matrix_height, margin = self._build_raw_matrix_layout(self._margin)

        pics_scaling_factor = min(float(self.width) / raw_matrix_width,
                                  (float(self.height) - self._texts_height) / raw_matrix_height)
        pics_x_offset = int(self.width - raw_matrix_width * pics_scaling_factor) // 2
        pics_y_offset = int((self.height - self._texts_height) - raw_matrix_height * pics_scaling_factor) // 2

        offset_generator = self._iter_raw_matrix_position(margin)

        for pil_image in self._images:
            cv_image = np.array(pil_image.convert('RGB'))
            if pics_scaling_factor > 0:
                cv_image = cv2.resize(cv_image, None, fx=pics_scaling_factor,
                                      fy=pics_scaling_factor, interpolation=cv2.INTER_AREA)
            height, width = cv_image.shape[:2]
            x_raw_offset, y_raw_offset = next(offset_generator)
            x_offset = pics_x_offset + int(pics_scaling_factor * x_raw_offset)
            y_offset = pics_y_offset + int(pics_scaling_factor * y_raw_offset)
            image[y_offset:(y_offset + height), x_offset:(x_offset + width)] = cv_image

        return image
