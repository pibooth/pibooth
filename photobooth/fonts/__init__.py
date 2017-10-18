# -*- coding: utf-8 -*-

import os.path as osp


def get_filename(name):
    """Return absolute path to a font definition file located in the current
    package.
    """
    return osp.join(osp.dirname(osp.abspath(__file__)), name)
