"""Plugin to log a message when entering in the 'wait' state."""

import pibooth
from pibooth.utils import LOGGER

__version__ = "1.0.0"

@pibooth.hookimpl
def state_wait_enter():
    LOGGER.info("Hello from '%s' plugin", __name__)
