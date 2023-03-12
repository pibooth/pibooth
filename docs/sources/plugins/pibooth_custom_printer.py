"""Pibooth plugin which customize printer to print several picture per page."""

import tempfile
import os.path as osp
from PIL import Image

import pibooth
from pibooth.printer import Printer
from pibooth.pictures import get_picture_factory


__version__ = "1.0.0"


class CustomPrinter(Printer):

    def __init__(self, name='default', max_pages=-1, options=None, pictures_per_page=1):
        super(CustomPrinter, self).__init__(name, max_pages, options)
        self.pictures_per_page = pictures_per_page

    def print_file(self, filename):
        """Send a file to the CUPS server to the default printer.
        """
        if self.pictures_per_page > 1:
            with tempfile.NamedTemporaryFile(suffix=osp.basename(filename)) as fp:
                picture = Image.open(filename)
                factory = get_picture_factory((picture,) * self.pictures_per_page)
                factory.set_margin(2)
                factory.save(fp.name)
                super(CustomPrinter, self).print_file(fp.name)
        else:
            super(CustomPrinter, self).print_file(filename)


@pibooth.hookimpl
def pibooth_configure(cfg):
    """Declare the new configuration options."""
    cfg.add_option('PRINTER', 'pictures_per_page', 1,
                   "Print 1, 2, 3 or 4 picture copies per page",
                   "Number of copies per page", [str(i) for i in range(1, 5)])


@pibooth.hookimpl
def pibooth_setup_printer(cfg):
    """Declare the new printer."""
    return CustomPrinter(cfg.get('PRINTER', 'printer_name'),
                         cfg.getint('PRINTER', 'max_pages'),
                         cfg.gettyped('PRINTER', 'printer_options'),
                         cfg.getint('PRINTER', 'pictures_per_page'))
