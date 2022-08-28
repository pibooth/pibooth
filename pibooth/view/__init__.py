# -*- coding: utf-8 -*-

from pibooth.view.pygame.window import PygameWindow
from pibooth.view.terminal.window import TerminalWindow

WINDOWS = {
    'terminal': TerminalWindow,
    'pygame': PygameWindow
}


def get_window(window_type, title, size, bg_color, text_color, debug=False):
    """Return the window according to the given type.

    :param window_type: type of the GUI used
    :type window_type: str
    :param title: title to display on the window
    :type title: str
    :param size: (width, height) to define the window size
    :type size: tuple
    :param bg_color: background RGB color
    :type bg_color: tuple
    :param text_color: type of the GUI used
    :type text_color: str
    """
    if window_type not in WINDOWS:
        raise ValueError(f"Unknown window type '{window_type}'")

    window_class = WINDOWS[window_type]

    if isinstance(size, (tuple, list)):
        return window_class(title, size, bg_color=bg_color, text_color=text_color, debug=debug)
    else:
        assert size == 'fullscreen', f"Invalid window size '{size}'"
        return window_class(title, bg_color=bg_color, text_color=text_color, debug=debug)
