# -*- coding: utf-8 -*-

from pibooth.view.nogui.window import NoGuiScene


def get_scene(name):
    """Return the scene according to the given name.

    :param name: name of the scene
    :type name: str
    """
    return NoGuiScene(name)
