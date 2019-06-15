# -*- coding: utf-8 -*-

"""Pibooth base states.
"""

import traceback
from pibooth.utils import LOGGER, BlockConsoleHandler


class State(object):

    app = None

    def __init__(self, name):
        self.name = name

    def entry_actions(self):
        """Perform actions when state is activated
        """
        pass

    def do_actions(self, events):
        """Perform periodic actions related to the state
        """
        pass

    def exit_actions(self):
        """Perform actions before state is deactivated
        """
        pass

    def validate_transition(self, events):
        """Return the name of the next state if can be activated
        """
        pass


class StateMachine(object):

    def __init__(self, application):
        self.states = {}
        self.failsafe_state = None
        self.active_state = None

        # Share the application to manage between states
        State.app = application

    def add_state(self, state):
        """Add a state to the internal dictionary.
        """
        self.states[state.name] = state

    def add_failsafe_state(self, state):
        """Add a state that will be call in case of exception.
        """
        self.failsafe_state = state
        self.states[state.name] = state

    def remove_state(self, state_name):
        """Remove a state to the internal dictionary.
        """
        state = self.states.pop(state_name, None)
        if state == self.failsafe_state:
            self.failsafe_state = None

    def process(self, events):
        """Let the current state do it's thing.
        """
        # Only continue if there is an active state
        if self.active_state is None:
            return

        try:
            # Perform the actions of the active state
            self.active_state.do_actions(events)

            # Check conditions to activate the next state
            new_state_name = self.active_state.validate_transition(events)
        except Exception as ex:
            if self.failsafe_state and self.active_state != self.failsafe_state:
                LOGGER.error(str(ex))
                if BlockConsoleHandler.is_debug():
                    traceback.print_exc()
                new_state_name = self.failsafe_state.name
            else:
                raise

        if new_state_name is not None:
            self.set_state(new_state_name)

    def set_state(self, state_name):
        """Change state machine's active state
        """
        try:
            # Perform any exit actions of the current state
            if self.active_state is not None:
                self.active_state.exit_actions()
        except Exception as ex:
            if self.failsafe_state and self.active_state != self.failsafe_state:
                LOGGER.error(str(ex))
                if BlockConsoleHandler.is_debug():
                    traceback.print_exc()
                state_name = self.failsafe_state.name
            else:
                raise

        if state_name not in self.states:
            raise ValueError('"{}" not in registered states...'.format(state_name))

        # Switch to the new state and perform its entry actions
        LOGGER.debug("Activate state '%s'", state_name)
        self.active_state = self.states[state_name]

        try:
            self.active_state.entry_actions()
        except Exception as ex:
            if self.failsafe_state and self.active_state != self.failsafe_state:
                LOGGER.error(str(ex))
                if BlockConsoleHandler.is_debug():
                    traceback.print_exc()
                self.set_state(self.failsafe_state.name)
            else:
                raise
