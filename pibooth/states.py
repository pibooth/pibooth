# -*- coding: utf-8 -*-

from pibooth.utils import LOGGER


class State(object):

    app = None

    def __init__(self, name, next_name=None):
        self.name = name
        self.next_name = next_name

    def entry_actions(self):
        """Perform actions when state is activated"""
        pass

    def do_actions(self, events):
        """Perform periodic actions related to the state"""
        pass

    def exit_actions(self):
        """Perform actions before state is deactivated"""
        pass

    def validate_transition(self, events):
        """Return the name of the next state if can be activated"""
        return self.next_name


class StateMachine(object):

    def __init__(self, application):
        self.states = {}
        self.active_state = None

        State.app = application

    def add_state(self, state):
        """Add a state to the internal dictionary"""
        self.states[state.name] = state

    def process(self, events):
        """Let the current state do it's thing"""

        # Only continue if there is an
        if self.active_state is None:
            return

        # Perform the actions of the active state and check conditions
        self.active_state.do_actions(events)

        new_state_name = self.active_state.validate_transition(events)
        if new_state_name is not None:
            self.set_state(new_state_name)

    def set_state(self, state_name):
        """Change state machine's active state"""

        # perform any exit actions of the current state
        if self.active_state is not None:
            self.active_state.exit_actions()

        if state_name not in self.states:
            raise ValueError('"{}" not in self.states...'.format(state_name))

        # Switch state and perform entry actions of new state
        LOGGER.debug("Activate state '%s'", state_name)
        self.active_state = self.states[state_name]
        self.active_state.entry_actions()
