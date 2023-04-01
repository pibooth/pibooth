"""Pibooth plugin to add a new state which a display 'Get Ready' text after each capture."""

import pibooth
from pibooth.utils import PollingTimer
from pibooth.view.pygame.sprites import BasePygameScene, TextSprite

__version__ = "0.0.2"


class MyScene(BasePygameScene):

    """Class to define a new visual scene.
    """

    def __init__(self):
        super().__init__()
        self.text = self.add_sprite(TextSprite("Get Ready!"))

    def resize(self, size):
        """Resize text when window is resized.
        """
        self.text.set_rect(*self.rect.inflate(-100, -100))


@pibooth.hookimpl
def pibooth_setup_states(machine):
    """Declare the new 'ready' state and associated scene.
    """
    machine.add_state('ready', MyScene())


@pibooth.hookimpl(hookwrapper=True)
def state_capture_validate(win):
    """Catch the next scene defined after a capture. If next state is
    'preview', then go back to 'ready' state.
    """
    # Catch next state defined by pibooth core components
    outcome = yield
    next_state = outcome.get_result()

    # If next state is 'preview' then replace it by 'ready' state
    if next_state == 'preview' and win.type == 'pygame':
        outcome.force_result('ready')


@pibooth.hookimpl(optionalhook=True)
def state_ready_enter(app):
    """Start a timer during which text is displayed.
    """
    app.readystate_timer = PollingTimer(5)


@pibooth.hookimpl(optionalhook=True)
def state_ready_validate(app):
    """Go to 'preview' state when timer is reached.
    """
    if app.readystate_timer.is_timeout():
        return 'preview'
