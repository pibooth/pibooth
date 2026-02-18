# -*- coding: utf-8 -*-

from pibooth.view.pygame.window import PygameWindow
from pibooth.view.nogui.window import NoGuiWindow, NoGuiScene
from pibooth.view.pygame.scenes.wait import WaitScene
from pibooth.view.pygame.scenes.choose import ChooseScene
from pibooth.view.pygame.scenes.chosen import ChosenScene
from pibooth.view.pygame.scenes.preview import PreviewScene
from pibooth.view.pygame.scenes.capture import CaptureScene
from pibooth.view.pygame.scenes.processing import ProcessingScene
from pibooth.view.pygame.scenes.print import PrintScene
from pibooth.view.pygame.scenes.finish import FinishScene
from pibooth.view.pygame.scenes.failsafe import FailsafeScene


WINDOWS = {
    'nogui': NoGuiWindow,
    'pygame': PygameWindow
}


SCENES = {
    'wait': WaitScene,
    'choose': ChooseScene,
    'chosen': ChosenScene,
    'preview': PreviewScene,
    'capture': CaptureScene,
    'processing': ProcessingScene,
    'print': PrintScene,
    'finish': FinishScene,
    'failsafe': FailsafeScene
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
    :param debug: display red indications for debugging purpose
    :type debug: bool
    """
    if window_type not in WINDOWS:
        raise ValueError(f"Unknown window type '{window_type}'")

    window_class = WINDOWS[window_type]

    if isinstance(size, (tuple, list)):
        window = window_class(title, size, background=background, text_color=text_color, debug=debug)
    else:
        assert size == 'fullscreen', f"Invalid window size '{size}'"
        window = window_class(title, background=background, text_color=text_color, debug=debug)

    window.type = window_type
    return window


def get_scene(window_type, name):
    """Return the scene according to the given name.

    :param window_type: type of the GUI used
    :type window_type: str
    :param name: name of the scene
    :type name: str
    """
    if window_type not in WINDOWS:
        raise ValueError(f"Unknown window type '{window_type}'")
    if name not in SCENES:
        raise ValueError(f"Unknown scene '{name}'")

    if window_type == 'nogui':
        return NoGuiScene()
    elif window_type == 'pygame':
        return SCENES[name]()
