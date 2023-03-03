# -*- coding: utf-8 -*-

import os
import os.path as osp
from pibooth import fonts
from pibooth.utils import LOGGER
from pibooth.pictures import sizing
from PIL import Image, ImageDraw

try:
    import cv2
    import numpy as np
except ImportError:
    cv2 = None


class PictureFactory(object):

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
        self._margin = 100
        self._margin_text = self._margin
        self._crop = False
        self._outlines = False
        self._images = images
        self._overlay_image = None
        self._background_color = (255, 255, 255)
        self._background_image = None

        self.name = self.__class__.__name__
        self.width = width
        self.height = height
        self.is_portrait = self.width < self.height

    def _iter_images(self):
        """Yield source images to concatenate.
        """
        raise NotImplementedError

    def _iter_images_rects(self):
        """Yield top-left coordinates and max size rectangle for each source image.

        :return: (image_x, image_y, image_width, image_height)
        :rtype: tuple
        """
        image_x = self._margin
        image_y = self._margin
        total_width = self.width - 2 * self._margin
        total_height = self.height - self._texts_height - 2 * self._margin

        if len(self._images) == 1:
            image_width = total_width
            image_height = total_height
        elif 2 <= len(self._images) < 4:
            if self.is_portrait:
                image_width = total_width
                image_height = (total_height - (len(self._images) - 1) * self._margin) // len(self._images)
            else:
                image_width = (total_width - (len(self._images) - 1) * self._margin) // len(self._images)
                image_height = total_height
        else:
            image_width = (total_width - self._margin) // 2
            image_height = (total_height - self._margin) // 2

        yield image_x, image_y, image_width, image_height

        if 2 <= len(self._images) < 4:
            if self.is_portrait:
                image_y += image_height + self._margin
            else:
                image_x += image_width + self._margin
            yield image_x, image_y, image_width, image_height

        if 3 <= len(self._images) < 4:
            if self.is_portrait:
                image_y += image_height + self._margin
            else:
                image_x += image_width + self._margin
            yield image_x, image_y, image_width, image_height

        if len(self._images) == 4:
            image_x += image_width + self._margin
            yield image_x, image_y, image_width, image_height
            image_y += image_height + self._margin
            image_x = self._margin
            yield image_x, image_y, image_width, image_height
            image_x += image_width + self._margin
            yield image_x, image_y, image_width, image_height

    def _iter_texts_rects(self, interline=None):
        """Yield top-left coordinates and max size rectangle for each text.

        :param interline: margin between each text line
        :type interline: int

        :return: (text_x, text_y, text_width, text_height)
        :rtype: tuple
        """
        if not interline:
            interline = 20

        text_x = self._margin_text
        text_y = self.height - self._texts_height
        total_width = self.width - 2 * self._margin_text
        total_height = self._texts_height - self._margin_text

        if self.is_portrait:
            text_height = (total_height - interline * (len(self._texts) - 1)) // (len(self._texts) + 1)
            for i in range(len(self._texts)):
                if i == 0:
                    yield text_x, text_y, total_width, 2 * text_height
                elif i == 1:
                    text_y += interline + 2 * text_height
                    yield text_x, text_y, total_width, text_height
                else:
                    text_y += interline + text_height
                    yield text_x, text_y, total_width, text_height
        else:
            text_width = (total_width - interline * (len(self._texts) - 1)) // len(self._texts)
            text_height = total_height // 2
            for i in range(len(self._texts)):
                if i == 0:
                    yield text_x, text_y, text_width, 2 * text_height
                else:
                    text_x += interline + text_width
                    yield text_x, text_y + (total_height - text_height) // 2, text_width, text_height

    def _image_resize_keep_ratio(self, image, max_w, max_h, crop=False):
        """Resize an image to fixed dimensions while keeping its aspect ratio.
        If crop = True, the image will be cropped to fit in the target dimensions.

        :return: image object, new width, new height
        :rtype: tuple
        """
        raise NotImplementedError

    def _image_paste(self, image, dest_image, pos_x, pos_y):
        """Paste the given image on the destination one.
        """
        raise NotImplementedError

    def _build_background(self):
        """Create an image with the given background.

        :return: image object which depends on the child class implementation.
        :rtype: object
        """
        raise NotImplementedError

    def _build_matrix(self, image):
        """Draw the images matrix on the given image.

        :param image: image object which depends on the child class implementation.
        :type image: object

        :return: image object which depends on the child class implementation.
        :rtype: object
        """
        offset_generator = self._iter_images_rects()
        count = 1
        for src_image in self._iter_images():
            pos_x, pos_y, max_w, max_h = next(offset_generator)
            src_image, width, height = self._image_resize_keep_ratio(src_image, max_w, max_h, self._crop)
            # Adjust position to have identical margin between borders and images
            if len(self._images) < 4:
                pos_x, pos_y = pos_x + (max_w - width) // 2, pos_y + (max_h - height) // 2
            elif count == 1:
                pos_x, pos_y = pos_x + (max_w - width) * 2 // 3, pos_y + (max_h - height) * 2 // 3
            elif count == 2:
                pos_x, pos_y = pos_x + (max_w - width) // 3, pos_y + (max_h - height) * 2 // 3
            elif count == 3:
                pos_x, pos_y = pos_x + (max_w - width) * 2 // 3, pos_y + (max_h - height) // 3
            else:
                pos_x, pos_y = pos_x + (max_w - width) // 3, pos_y + (max_h - height) // 3

            self._image_paste(src_image, image, pos_x, pos_y)
            count += 1
        return image

    def _build_final_image(self, image):
        """Create the final PIL image and set it to the _final attribute.

        :param image: image object which depends on the child class implementation.
        :type image: object

        :return: PIL.Image instance
        :rtype: object
        """
        raise NotImplementedError

    def _build_texts(self, image):
        """Draw texts on a PIL image (PIL is used instead of OpenCV
        because it is able to draw any fonts without ext).

        :param image: PIL.Image instance
        :type image: object
        """
        offset_generator = self._iter_texts_rects()
        draw = ImageDraw.Draw(image)
        for text, font_name, color, align in self._texts:
            text_x, text_y, max_width, max_height = next(offset_generator)
            if not text:  # Empty string: go to next text position
                continue
            # Use PIL to draw text because better support for fonts than OpenCV
            font = fonts.get_pil_font(text, font_name, max_width, max_height)
            _, text_height = font.getsize(text)
            (text_width, _baseline), (offset_x, offset_y) = font.font.getsize(text)
            if align == self.CENTER:
                text_x += (max_width - text_width) // 2
            elif align == self.RIGHT:
                text_x += (max_width - text_width)

            draw.text((text_x - offset_x // 2,
                       text_y + (max_height - text_height) // 2 - offset_y // 2),
                      text, color, font=font)

    def _build_outlines(self, image):
        """Build rectangle around each elements. This method is only for
        debuging purpose.

        :param image: PIL.Image instance
        :type image: object
        """
        draw = ImageDraw.Draw(image)
        for x, y, w, h in self._iter_images_rects():
            draw.rectangle(((x, y), (x + w, y + h)), outline='red')
        if self._texts:
            for x, y, w, h in self._iter_texts_rects():
                draw.rectangle(((x, y), (x + w, y + h)), outline='red')

    def add_text(self, text, font_name, color, align=CENTER):
        """Add a new text.

        :param text: text to draw
        :type text: str
        :param font_name: name or path to font file
        :type font_name: str
        :param color: RGB tuple
        :type color: tuple
        :param align: text alignment: left, right or center
        :type align: str
        """
        assert align in [self.CENTER, self.RIGHT, self.LEFT], "Unknown aligment '{}'".format(align)
        self._texts.append((text, fonts.get_filename(font_name), color, align))
        if self.is_portrait:
            self._texts_height = int(self.height // 6)
        else:
            self._texts_height = int(self.height // 8)
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
            if not osp.isfile(color_or_path):
                raise ValueError("Invalid background image '{}'".format(color_or_path))
            self._background_image = color_or_path
        self._final = None  # Force rebuild

    def set_overlay(self, image_path):
        """Set an image that will be paste over the final picture.

        :param image_path: image path
        :type image_path: str
        """
        if not osp.isfile(image_path):
            raise ValueError("Invalid background image '{}'".format(image_path))
        self._overlay_image = image_path
        self._final = None  # Force rebuild

    def set_margin(self, margin, margin_text=None):
        """Set margin between concatenated images.

        :param margin: margin in pixels
        :type margin: int
        :param margin_text: margin between texts in pixels
        :type margin_text: int
        """
        self._margin = margin
        if margin_text is None:
            self._margin_text = margin
        else:
            self._margin_text = margin_text
        self._final = None  # Force rebuild

    def set_cropping(self, crop=True):
        """Enable the cropping of source images it order to fit to the final
        size. However some parts of the images will be lost.

        :param crop: enable / disable cropping
        :type crop: bool
        """
        self._crop = crop
        self._final = None  # Force rebuild

    def set_outlines(self, outlines=True):
        """Draw outlines for each rectangle available for drawing
        images and texts.

        :param outlines: enable / disable outlines
        :type outlines: bool
        """
        self._outlines = outlines
        self._final = None  # Force rebuild

    def build(self, rebuild=False):
        """Build the final image or doas nothing if the final image
        has already been built previously.

        :param rebuild: force re-build image
        :type rebuild: bool

        :return: PIL.Image instance
        :rtype: object
        """
        if not self._final or rebuild:

            LOGGER.info("Use %s to create background", self.name)
            image = self._build_background()

            LOGGER.info("Use %s to concatenate images", self.name)
            image = self._build_matrix(image)

            LOGGER.info("Use %s to assemble final image", self.name)
            self._final = self._build_final_image(image)

            LOGGER.info("Use %s to draw texts", self.name)
            self._build_texts(self._final)

            if self._outlines:
                LOGGER.info("Use %s to outline boundary borders", self.name)
                self._build_outlines(self._final)

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
        LOGGER.info("Save image '%s'", path)
        image.save(path)
        return image


class PilPictureFactory(PictureFactory):

    def _image_resize_keep_ratio(self, image, max_w, max_h, crop=False):
        """See upper class description.
        """
        if crop:
            width, height = sizing.new_size_keep_aspect_ratio(image.size, (max_w, max_h), 'outer')
            image = image.resize((width, height), Image.ANTIALIAS)
            image = image.crop(sizing.new_size_by_croping(image.size, (max_w, max_h)))
        else:
            width, height = sizing.new_size_keep_aspect_ratio(image.size, (max_w, max_h), 'inner')
            image = image.resize((width, height), Image.ANTIALIAS)
        return image, image.size[0], image.size[1]

    def _image_paste(self, image, dest_image, pos_x, pos_y):
        """See upper class description.
        """
        dest_image.paste(image, (pos_x, pos_y))

    def _iter_images(self):
        """See upper class description.
        """
        for image in self._images:
            yield image

    def _build_final_image(self, image):
        """See upper class description.
        """
        if self._overlay_image:
            overlay = Image.open(self._overlay_image).convert('RGBA')
            overlay, _, _ = self._image_resize_keep_ratio(overlay, self.width, self.height, True)
            image = Image.alpha_composite(image.convert('RGBA'), overlay)
            image = image.convert('RGB')
        return image

    def _build_background(self):
        """See upper class description.
        """
        if self._background_image:
            bg = Image.open(self._background_image)
            image, _, _ = self._image_resize_keep_ratio(bg, self.width, self.height, True)
        else:
            image = Image.new('RGB', (self.width, self.height), color=self._background_color)
        return image


class OpenCvPictureFactory(PictureFactory):

    def _image_resize_keep_ratio(self, image, max_w, max_h, crop=False):
        """See upper class description.
        """
        inter = cv2.INTER_AREA
        height, width = image.shape[:2]

        source_aspect_ratio = float(width) / height
        target_aspect_ratio = float(max_w) / max_h

        if crop:
            if source_aspect_ratio <= target_aspect_ratio:
                h_cropped = int(width / target_aspect_ratio)
                x_offset = 0
                y_offset = int((float(height) - h_cropped) / 2)
                cropped = image[y_offset:(y_offset + h_cropped), x_offset:width]
            else:
                w_cropped = int(height * target_aspect_ratio)
                x_offset = int((float(width) - w_cropped) / 2)
                y_offset = 0
                cropped = image[y_offset:height, x_offset:(x_offset + w_cropped)]
            image = cv2.resize(cropped, (max_w, max_h), interpolation=inter)
        else:
            width, height = sizing.new_size_keep_aspect_ratio((width, height), (max_w, max_h), 'inner')
            image = cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)
        return image, image.shape[1], image.shape[0]

    def _image_paste(self, image, dest_image, pos_x, pos_y):
        """See upper class description.
        """
        height, width = image.shape[:2]
        dest_image[pos_y:(pos_y + height), pos_x:(pos_x + width)] = image

    def _iter_images(self):
        """See upper class description.
        """
        for image in self._images:
            yield np.array(image.convert('RGB'))

    def _build_final_image(self, image):
        """See upper class description.
        """
        if self._overlay_image:
            overlay = cv2.cvtColor(cv2.imread(self._overlay_image, cv2.IMREAD_UNCHANGED), cv2.COLOR_BGR2RGBA)
            overlay, _, _ = self._image_resize_keep_ratio(overlay, self.width, self.height, True)

            x, y = 0, 0
            image_width = image.shape[1]
            image_height = image.shape[0]

            h, w = overlay.shape[0], overlay.shape[1]

            if x + w > image_width:
                w = image_width - x
                overlay = overlay[:, :w]

            if y + h > image_height:
                h = image_height - y
                overlay = overlay[:h]

            if overlay.shape[2] < 4:
                overlay = np.concatenate(
                    [
                        overlay,
                        np.ones((overlay.shape[0], overlay.shape[1], 1), dtype=overlay.dtype) * 255
                    ],
                    axis=2,
                )

            overlay_image = overlay[..., :3]
            mask = overlay[..., 3:] / 255.0

            image[y:y+h, x:x+w] = (1.0 - mask) * image[y:y+h, x:x+w] + mask * overlay_image

        return Image.fromarray(image)

    def _build_background(self):
        """See upper class description.
        """
        if self._background_image:
            bg = cv2.cvtColor(cv2.imread(self._background_image), cv2.COLOR_BGR2RGB)
            image, _, _ = self._image_resize_keep_ratio(bg, self.width, self.height, True)
        else:
            # Small optimization for all white or all black (or all grey...) background
            if self._background_color[0] == self._background_color[1] and self._background_color[1] == self._background_color[2]:
                image = np.full((self.height, self.width, 3), self._background_color[0], np.uint8)
            else:
                image = np.zeros((self.height, self.width, 3), np.uint8)
                image[:] = (self._background_color[0], self._background_color[1], self._background_color[2])

        return image
