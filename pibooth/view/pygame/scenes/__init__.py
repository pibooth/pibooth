# -*- coding: utf-8 -*-

from pibooth.view.pygame.scenes.wait import WaitScene
from pibooth.view.pygame.scenes.choose import ChooseScene
from pibooth.view.pygame.scenes.chosen import ChosenScene
from pibooth.view.pygame.scenes.preview import PreviewScene
from pibooth.view.pygame.scenes.capture import CaptureScene
from pibooth.view.pygame.scenes.processing import ProcessingScene
from pibooth.view.pygame.scenes.print import PrintScene
from pibooth.view.pygame.scenes.finish import FinishScene
from pibooth.view.pygame.scenes.failsafe import FailsafeScene

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


def get_scene(name):
    """Return the scene according to the given name.

    :param name: name of the scene
    :type name: str
    """
    if name not in SCENES:
        raise ValueError(f"Unknown scene '{name}'")

    return SCENES[name](name)
