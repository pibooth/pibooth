# -*- coding: utf-8 -*-

import pluggy

hookspec = pluggy.HookspecMarker('pibooth')


#--- FailSafe State -----------------------------------------------------------


@hookspec
def state_failsafe_enter(cfg, app):
    """Actions performed when application enter in FailSafe state.

    :param cfg: application cfg
    :param app: application instance
    """


@hookspec
def state_failsafe_do(cfg, app, events):
    """Actions performed when application is in FailSafe state.
    This hook is called in a loop until the application can switch
    to the next state.

    :param cfg: application cfg
    :param app: application instance
    :param events: pygame events generated since last call
    """


@hookspec(firstresult=True)
def state_failsafe_validate(cfg, app, events):
    """Return the next state name if application can switch to it
    else return None.

    :param cfg: application cfg
    :param app: application instance
    :param events: pygame events generated since last call
    """


@hookspec
def state_failsafe_exit(cfg, app):
    """Actions performed when application exit FailSafe state.

    :param cfg: application cfg
    :param app: application instance
    """


#--- Wait State ---------------------------------------------------------------


@hookspec
def state_wait_enter(cfg, app):
    """Actions performed when application enter in Wait state.

    :param cfg: application cfg
    :param app: application instance
    """


@hookspec
def state_wait_do(cfg, app, events):
    """Actions performed when application is in Wait state.
    This hook is called in a loop until the application can switch
    to the next state.

    :param cfg: application cfg
    :param app: application instance
    :param events: pygame events generated since last call
    """


@hookspec(firstresult=True)
def state_wait_validate(cfg, app, events):
    """Return the next state name if application can switch to it
    else return None.

    :param cfg: application cfg
    :param app: application instance
    :param events: pygame events generated since last call
    """


@hookspec
def state_wait_exit(cfg, app):
    """Actions performed when application exit Wait state.

    :param cfg: application cfg
    :param app: application instance
    """


#--- Choose State -------------------------------------------------------------


@hookspec
def state_choose_enter(cfg, app):
    """Actions performed when application enter in Choose state.

    :param cfg: application cfg
    :param app: application instance
    """


@hookspec
def state_choose_do(cfg, app, events):
    """Actions performed when application is in Choose state.
    This hook is called in a loop until the application can switch
    to the next state.

    :param cfg: application cfg
    :param app: application instance
    :param events: pygame events generated since last call
    """


@hookspec(firstresult=True)
def state_choose_validate(cfg, app, events):
    """Return the next state name if application can switch to it
    else return None.

    :param cfg: application cfg
    :param app: application instance
    :param events: pygame events generated since last call
    """


@hookspec
def state_choose_exit(cfg, app):
    """Actions performed when application exit Choose state.

    :param cfg: application cfg
    :param app: application instance
    """


#--- Chosen State -------------------------------------------------------------


@hookspec
def state_chosen_enter(cfg, app):
    """Actions performed when application enter in Chosen state.

    :param cfg: application cfg
    :param app: application instance
    """


@hookspec
def state_chosen_do(cfg, app, events):
    """Actions performed when application is in Chosen state.
    This hook is called in a loop until the application can switch
    to the next state.

    :param cfg: application cfg
    :param app: application instance
    :param events: pygame events generated since last call
    """


@hookspec(firstresult=True)
def state_chosen_validate(cfg, app, events):
    """Return the next state name if application can switch to it
    else return None.

    :param cfg: application cfg
    :param app: application instance
    :param events: pygame events generated since last call
    """


@hookspec
def state_chosen_exit(cfg, app):
    """Actions performed when application exit Chosen state.

    :param cfg: application cfg
    :param app: application instance
    """


#--- Preview State ------------------------------------------------------------


@hookspec
def state_preview_enter(cfg, app):
    """Actions performed when application enter in Preview state.

    :param cfg: application cfg
    :param app: application instance
    """


@hookspec
def state_preview_do(cfg, app, events):
    """Actions performed when application is in Preview state.
    This hook is called in a loop until the application can switch
    to the next state.

    :param cfg: application cfg
    :param app: application instance
    :param events: pygame events generated since last call
    """


@hookspec(firstresult=True)
def state_preview_validate(cfg, app, events):
    """Return the next state name if application can switch to it
    else return None.

    :param cfg: application cfg
    :param app: application instance
    :param events: pygame events generated since last call
    """


@hookspec
def state_preview_exit(cfg, app):
    """Actions performed when application exit Preview state.

    :param cfg: application cfg
    :param app: application instance
    """


#--- Capture State ------------------------------------------------------------


@hookspec
def state_capture_enter(cfg, app):
    """Actions performed when application enter in Capture state.

    :param cfg: application cfg
    :param app: application instance
    """


@hookspec
def state_capture_do(cfg, app, events):
    """Actions performed when application is in Capture state.
    This hook is called in a loop until the application can switch
    to the next state.

    :param cfg: application cfg
    :param app: application instance
    :param events: pygame events generated since last call
    """


@hookspec(firstresult=True)
def state_capture_validate(cfg, app, events):
    """Return the next state name if application can switch to it
    else return None.

    :param cfg: application cfg
    :param app: application instance
    :param events: pygame events generated since last call
    """


@hookspec
def state_capture_exit(cfg, app):
    """Actions performed when application exit Capture state.

    :param cfg: application cfg
    :param app: application instance
    """


#--- Processing State ---------------------------------------------------------


@hookspec
def state_processing_enter(cfg, app):
    """Actions performed when application enter in Processing state.

    :param cfg: application cfg
    :param app: application instance
    """


@hookspec
def state_processing_do(cfg, app, events):
    """Actions performed when application is in Processing state.
    This hook is called in a loop until the application can switch
    to the next state.

    :param cfg: application cfg
    :param app: application instance
    :param events: pygame events generated since last call
    """


@hookspec(firstresult=True)
def state_processing_validate(cfg, app, events):
    """Return the next state name if application can switch to it
    else return None.

    :param cfg: application cfg
    :param app: application instance
    :param events: pygame events generated since last call
    """


@hookspec
def state_processing_exit(cfg, app):
    """Actions performed when application exit Processing state.

    :param cfg: application cfg
    :param app: application instance
    """


#--- PrintView State ----------------------------------------------------------


@hookspec
def state_print_enter(cfg, app):
    """Actions performed when application enter in Print state.

    :param cfg: application cfg
    :param app: application instance
    """


@hookspec
def state_print_do(cfg, app, events):
    """Actions performed when application is in Print state.
    This hook is called in a loop until the application can switch
    to the next state.

    :param cfg: application cfg
    :param app: application instance
    :param events: pygame events generated since last call
    """


@hookspec(firstresult=True)
def state_print_validate(cfg, app, events):
    """Return the next state name if application can switch to it
    else return None.

    :param cfg: application cfg
    :param app: application instance
    :param events: pygame events generated since last call
    """


@hookspec
def state_print_exit(cfg, app):
    """Actions performed when application exit Print state.

    :param cfg: application cfg
    :param app: application instance
    """


#--- Finish State -------------------------------------------------------------


@hookspec
def state_finish_enter(cfg, app):
    """Actions performed when application enter in Finish state.

    :param cfg: application cfg
    :param app: application instance
    """


@hookspec
def state_finish_do(cfg, app, events):
    """Actions performed when application is in Finish state.
    This hook is called in a loop until the application can switch
    to the next state.

    :param cfg: application cfg
    :param app: application instance
    :param events: pygame events generated since last call
    """


@hookspec(firstresult=True)
def state_finish_validate(cfg, app, events):
    """Return the next state name if application can switch to it
    else return None.

    :param cfg: application cfg
    :param app: application instance
    :param events: pygame events generated since last call
    """


@hookspec
def state_finish_exit(cfg, app):
    """Actions performed when application exit Finish state.

    :param cfg: application cfg
    :param app: application instance
    """
