# -*- coding: utf-8 -*-

from pibooth.view.pygame.scenes.preview import PreviewScene


class CaptureScene(PreviewScene):

    """Scene displayed while a capture is taken. It has the layout of the
    preview scene, so that the last preview frame stays at the same place
    during the capture.
    """

    FLASH_COLOR = (255, 255, 255)

    def __init__(self):
        super().__init__()
        self.is_flash_on = False
        self.saved_skin = None

    def set_flash(self, enable=True):
        """Light the background up, or put it back as it was. Only the
        background flashes: the image and the counter stay displayed.

        The background sprite is shared by all the scenes, the window puts the
        configured one back at each scene change.

        :param enable: turn the flash on / off
        :type enable: bool
        """
        if enable:
            if self.background.get_skin() != self.FLASH_COLOR:
                self.saved_skin = self.background.get_skin()
                self.background.set_skin(self.FLASH_COLOR)
            self.is_flash_on = True
        else:
            if self.is_flash_on and self.saved_skin is not None \
                    and self.background.get_skin() == self.FLASH_COLOR:
                self.background.set_skin(self.saved_skin)
            self.is_flash_on = False
