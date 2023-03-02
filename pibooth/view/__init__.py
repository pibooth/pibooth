# -*- coding: utf-8 -*-

from pibooth.view.pygame.window import PygameWindow
from pibooth.view.nogui.window import NoGuiWindow

WINDOWS = {
    'nogui': NoGuiWindow,
    'pygame': PygameWindow
}


def get_window(window_type, title, size, background, text_color, debug=False):
    """Return the window according to the given type.

    :param window_type: type of the GUI used
    :type window_type: str
    :param title: title to display on the window
    :type title: str
    :param size: (width, height) to define the window size
    :type size: tuple
    :param background: background image path of RGB color tuple
    :type background: tuple or str
    :param text_color: text RGB color tuple
    :type text_color: tuple
    :param debug: display red indictions for debugging purpose
    :type debug: bool
    """
    if window_type not in WINDOWS:
        raise ValueError(f"Unknown window type '{window_type}'")

    window_class = WINDOWS[window_type]

    if isinstance(size, (tuple, list)):
        return window_class(title, size, background=background, text_color=text_color, debug=debug)
    else:
        assert size == 'fullscreen', f"Invalid window size '{size}'"
        return window_class(title, background=background, text_color=text_color, debug=debug)
