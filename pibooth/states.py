# -*- coding: utf-8 -*-

import logging
import traceback
from functools import wraps
from pibooth.utils import LOGGER


def failsafe(func):
    """Ensure fail safe mode.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        machine = args[0]
        if not machine.failsafe_state or machine.failsafe_state == machine.active_state:
            return func(*args, **kwargs)
        else:
            try:
                return func(*args, **kwargs)
            except Exception as ex:
                LOGGER.error(str(ex))
                if LOGGER.getEffectiveLevel() < logging.INFO and machine.failsafe_state != machine.active_state:
                    traceback.print_exc()
            if machine.active_state is not None:
                machine.active_state.exit_actions()
            machine.active_state = machine.failsafe_state
            machine.active_state.entry_actions()

    return wrapper


class State(object):

    app = None

    def __init__(self, name, next_name=None):
        self.name = name
        self.next_name = next_name

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
        return self.next_name


class StateMachine(object):

    def __init__(self, application):
        self.states = {}
        self.failsafe_state = None
        self.active_state = None

        # Share the application to manage between states
        State.app = application

    def add_state(self, state):
        """Add a state to the internal dictionary
        """
        self.states[state.name] = state

    def add_failsafe_state(self, state):
        """Add a state that will be call in case of exception.
        """
        self.failsafe_state = state
        self.states[state.name] = state

    @failsafe
    def process(self, events):
        """Let the current state do it's thing
        """
        # Only continue if there is an active state
        if self.active_state is None:
            return

        # Perform the actions of the active state
        self.active_state.do_actions(events)

        # Check conditions to activate the next state
        new_state_name = self.active_state.validate_transition(events)
        if new_state_name is not None:
            self.set_state(new_state_name)

    @failsafe
    def set_state(self, state_name):
        """Change state machine's active state
        """
        # Perform any exit actions of the current state
        if self.active_state is not None:
            self.active_state.exit_actions()

        if state_name not in self.states:
            raise ValueError('"{}" not in registered states...'.format(state_name))

        # Switch to the new state and perform its entry actions
        LOGGER.debug("Activate state '%s'", state_name)
        self.active_state = self.states[state_name]
        self.active_state.entry_actions()
