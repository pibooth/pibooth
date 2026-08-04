# -*- coding: utf-8 -*-
"""Minimal enter/do/validate/exit state machine (pattern inspired by pibooth).

Each :class:`State` represents one screen/phase of the booth flow. On every
frame the active state's ``do`` is called, followed by ``validate`` which
returns the name of the next state to transition to, or ``None`` to stay.
Any exception raised by a state is caught and routed to the configured
fail-safe state, which is responsible for showing an error and eventually
returning to idle.
"""

from __future__ import annotations

import logging
from typing import Dict, Optional

LOGGER = logging.getLogger("fotobox.session.state_machine")


class State:
    name: str = ""

    def enter(self, ctx) -> None:
        """Called once when this state becomes active."""

    def do(self, ctx, dt: float) -> None:
        """Called every frame while this state is active."""

    def validate(self, ctx) -> Optional[str]:
        """Return the next state name to switch to, or None to stay."""
        return None

    def exit(self, ctx) -> None:
        """Called once when leaving this state."""


class StateMachine:

    def __init__(self, ctx, failsafe_state_name: str = "failsafe"):
        self._ctx = ctx
        self._states: Dict[str, State] = {}
        self._failsafe_state_name = failsafe_state_name
        self._active_state: Optional[State] = None

    def add_state(self, state: State) -> None:
        self._states[state.name] = state

    @property
    def active_state_name(self) -> Optional[str]:
        return self._active_state.name if self._active_state else None

    def start(self, initial_state_name: str) -> None:
        self.set_state(initial_state_name)

    def set_state(self, name: str) -> None:
        if name not in self._states:
            raise ValueError("Unbekannter State: '{}'".format(name))

        if self._active_state is not None:
            try:
                self._active_state.exit(self._ctx)
            except Exception:
                LOGGER.exception("Fehler beim Verlassen von State '%s'",
                                  self._active_state.name)

        LOGGER.debug("Wechsle zu State '%s'", name)
        self._active_state = self._states[name]

        try:
            self._active_state.enter(self._ctx)
        except Exception:
            LOGGER.exception("Fehler beim Betreten von State '%s'", name)
            if name != self._failsafe_state_name:
                self.set_state(self._failsafe_state_name)

    def process(self, dt: float) -> None:
        if self._active_state is None:
            return
        try:
            self._active_state.do(self._ctx, dt)
            next_name = self._active_state.validate(self._ctx)
        except Exception as exc:
            LOGGER.exception("Fehler im State '%s'", self._active_state.name)
            self._ctx.session.error_message = str(exc)
            if self._active_state.name != self._failsafe_state_name:
                self.set_state(self._failsafe_state_name)
            return

        if next_name is not None:
            self.set_state(next_name)
