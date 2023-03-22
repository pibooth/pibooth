# -*- coding: utf-8 -*-

"""Pibooth base states.
"""

import time
from pibooth.utils import LOGGER, BlockConsoleHandler


class StateMachine(object):

    def __init__(self, plugins_manager, configuration, application, window):
        self.states = set()
        self.failsafe_state = None
        self.active_state = None
        self.pm = plugins_manager

        # Shared variables between states
        self.app = application
        self.win = window
        self.cfg = configuration

        self._start_time = time.time()

    def add_state(self, name, scene):
        """Add a state to the internal dictionary.
        """
        self.states.add(name)
        scene.name = name
        self.win.add_scene(scene)

    def add_failsafe_state(self, name, scene):
        """Add a state that will be called in case of exception.
        """
        self.failsafe_state = name
        self.states.add(name)
        scene.name = name
        self.win.add_scene(scene)

    def remove_state(self, name):
        """Remove a state from the internal dictionary.
        """
        self.states.discard(name)
        self.win.remove_scene(name)
        if name == self.failsafe_state:
            self.failsafe_state = None

    def process(self, events):
        """Let the current state do it's thing.
        """
        # Only continue if there is an active state
        if self.active_state is None:
            return

        try:
            # Perform the actions of the active state
            hook = self.pm.subset_hook_caller(f'state_{self.active_state}_do', optional=True)
            hook(cfg=self.cfg, app=self.app, win=self.win, events=events)

            # Check conditions to activate the next state
            hook = self.pm.subset_hook_caller(f'state_{self.active_state}_validate', optional=True)
            new_state_name = hook(cfg=self.cfg, app=self.app, win=self.win, events=events)
        except Exception as ex:
            if self.failsafe_state and self.active_state != self.failsafe_state:
                LOGGER.error(str(ex))
                LOGGER.debug('Back to failsafe state due to error:', exc_info=True)
                new_state_name = self.failsafe_state
            else:
                raise

        if new_state_name not in (None, [], ()):
            if isinstance(new_state_name, (tuple, list)):
                new_state_name = new_state_name[-1]
            self.set_state(new_state_name)

    def set_state(self, state_name):
        """Change state machine's active state
        """
        try:
            # Perform any exit actions of the current state
            if self.active_state is not None:
                hook = self.pm.subset_hook_caller(f'state_{self.active_state}_exit', optional=True)
                hook(cfg=self.cfg, app=self.app, win=self.win)
                BlockConsoleHandler.dedent()
                LOGGER.debug("took %0.3f seconds", time.time() - self._start_time)
        except Exception as ex:
            if self.failsafe_state and self.active_state != self.failsafe_state:
                LOGGER.error(str(ex))
                LOGGER.debug('Back to failsafe state due to error:', exc_info=True)
                state_name = self.failsafe_state
            else:
                raise

        if state_name not in self.states:
            raise ValueError(f'"{state_name}" not in registered states...')

        # Switch to the new state and perform its entry actions
        BlockConsoleHandler.indent()
        self._start_time = time.time()
        LOGGER.debug("Activate state '%s'", state_name)
        self.active_state = state_name

        try:
            self.win.set_scene(self.active_state)
            hook = self.pm.subset_hook_caller(f'state_{self.active_state}_enter', optional=True)
            hook(cfg=self.cfg, app=self.app, win=self.win)
        except Exception as ex:
            if self.failsafe_state and self.active_state != self.failsafe_state:
                LOGGER.error(str(ex))
                LOGGER.debug('Back to failsafe state due to error:', exc_info=True)
                self.set_state(self.failsafe_state)
            else:
                raise
