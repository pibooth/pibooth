"""Pibooth plugin which return the first raw capture as final picture."""

import pibooth
from pibooth.pictures.factory import PictureFactory


__version__ = "1.0.0"


class IdlePictureFactory(PictureFactory):

    def build(self, rebuild=False):
        return self._images[0]


@pibooth.hookimpl
def pibooth_setup_picture_factory(factory):
    return IdlePictureFactory(factory.width, factory.height, *factory._images)
