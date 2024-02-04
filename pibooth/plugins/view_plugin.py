# -*- coding: utf-8 -*-

import pibooth
from pibooth import evts
from pibooth.view import get_scene
from pibooth.utils import LOGGER, get_crash_message, PollingTimer


class ViewPlugin:

    """Plugin to manage the pibooth window dans transitions.
    """

    __name__ = 'pibooth-core:view'

    def __init__(self, plugin_manager):
        self._pm = plugin_manager
        self.capture_count = 0
        self.capture_finished = False
        self.forgotten = False
        # Seconds to display the failed message
        self.failed_view_timer = PollingTimer(2)
        # Seconds between each animated frame
        self.animated_frame_timer = PollingTimer(0)
        # Seconds before going back to the start
        self.choose_timer = PollingTimer(30)
        # Seconds to display the selected layout
        self.layout_timer = PollingTimer(4)
        # Seconds to display the print view
        self.print_view_timer = PollingTimer(0)
        # Seconds to display the finished view
        self.finish_timer = PollingTimer(1)

    @pibooth.hookimpl
    def pibooth_setup_states(self, win, machine):
        for name in ('wait', 'choose', 'chosen', 'preview', 'capture', 'processing', 'print', 'finish'):
            machine.add_state(name, get_scene(win.type, name))

    @pibooth.hookimpl
    def state_failsafe_enter(self):
        self.failed_view_timer.start()
        LOGGER.error(get_crash_message())

    @pibooth.hookimpl
    def state_failsafe_validate(self):
        if self.failed_view_timer.is_timeout():
            return 'wait'

    @pibooth.hookimpl
    def state_wait_enter(self, cfg, app, win):
        self.forgotten = False
        if app.previous_animated:
            previous_picture = next(app.previous_animated)
            self.animated_frame_timer.start(cfg.getfloat('WINDOW', 'animate_delay'))
        else:
            previous_picture = app.previous_picture

        win.scene.set_image(previous_picture)
        win.scene.update_print_action(app.previous_picture and app.printer.is_ready()
                                      and app.count.remaining_duplicates > 0)
        win.set_system_status(len(app.printer.get_all_tasks()), not app.printer.is_ready(),
                              app.count.printed, app.count.taken)

    @pibooth.hookimpl
    def state_wait_do(self, app, win, events):
        if app.previous_animated and self.animated_frame_timer.is_timeout():
            win.scene.update_print_action(app.printer.is_ready() and app.count.remaining_duplicates > 0)
            self.animated_frame_timer.start()
            win.scene.set_image(next(app.previous_animated))

        if evts.find_event(events, evts.EVT_PIBOOTH_PRINTER_UPDATE):
            win.set_system_status(len(app.printer.get_all_tasks()), not app.printer.is_ready(),
                                  app.count.printed, app.count.taken)

        if evts.find_event(events, evts.EVT_PIBOOTH_PRINT):
            win.scene.update_print_action(app.printer.is_ready() and app.count.remaining_duplicates > 0)

    @pibooth.hookimpl
    def state_wait_validate(self, cfg, app, events):
        if evts.find_event(events, evts.EVT_PIBOOTH_CAPTURE):
            if len(app.capture_choices) > 1:
                return 'choose'
            if cfg.getfloat('WINDOW', 'chosen_delay') > 0:
                return 'chosen'
            if cfg.getint('WINDOW', 'preview_delay') > 0:
                return 'preview'
            return 'capture'

    @pibooth.hookimpl
    def state_choose_enter(self, app, win):
        LOGGER.info("Show picture choice (nothing selected)")
        win.scene.set_choices(app.capture_choices)
        self.choose_timer.start()

    @pibooth.hookimpl
    def state_choose_do(self, app, win, events):
        if evts.find_event(events, evts.EVT_PIBOOTH_CAPTURE):
            app.capture_nbr = win.scene.get_selection()
        if evts.find_event(events, evts.EVT_PIBOOTH_PRINT):
            win.scene.next()

    @pibooth.hookimpl
    def state_choose_validate(self, cfg, app):
        if app.capture_nbr:
            if cfg.getfloat('WINDOW', 'chosen_delay') > 0:
                return 'chosen'
            else:
                return 'preview'
        elif self.choose_timer.is_timeout():
            return 'wait'

    @pibooth.hookimpl
    def state_chosen_enter(self, cfg, app, win):
        LOGGER.info("Show picture choice (%s captures selected)", app.capture_nbr)
        win.scene.set_selected_choice(app.capture_nbr)
        self.layout_timer.start(cfg.getfloat('WINDOW', 'chosen_delay'))

    @pibooth.hookimpl
    def state_chosen_validate(self):
        if self.layout_timer.is_timeout():
            return 'preview'

    @pibooth.hookimpl
    def state_preview_enter(self, app, win):
        win.scene.set_capture_number(self.capture_count + 1, app.capture_nbr)

    @pibooth.hookimpl
    def state_preview_do(self, win, events):
        event = evts.find_event(events, evts.EVT_PIBOOTH_CAM_PREVIEW)
        if event:
            win.scene.set_image(event.result, stream=True)

    @pibooth.hookimpl
    def state_capture_enter(self, cfg, app, win):
        self.capture_finished = False
        if cfg.getboolean('WINDOW', 'flash'):
            win.scene.trigger_flash()
        win.scene.set_capture_number(self.capture_count + 1, app.capture_nbr)

    @pibooth.hookimpl
    def state_capture_do(self, events):
        event = evts.find_event(events, evts.EVT_PIBOOTH_CAM_CAPTURE)
        if event:
            self.capture_finished = True
            self.capture_count += 1

    @pibooth.hookimpl
    def state_capture_validate(self, cfg, app, win):
        if self.capture_finished and (not cfg.getboolean('WINDOW', 'flash') or win.scene.count_flash >= 2):
            if self.capture_count >= app.capture_nbr:
                return 'processing'
            if cfg.getint('WINDOW', 'preview_delay') > 0:
                return 'preview'
            return 'capture'

    @pibooth.hookimpl
    def state_processing_enter(self):
        self.capture_count = 0

    @pibooth.hookimpl
    def state_processing_validate(self, cfg, app):
        if app.previous_picture:  # Processing is finished
            if app.printer.is_ready() and cfg.getfloat('PRINTER', 'printer_delay') > 0\
                    and app.count.remaining_duplicates > 0:
                return 'print'
            return 'finish'  # Can not print

    @pibooth.hookimpl
    def state_print_enter(self, cfg, app, win):
        LOGGER.info("Display the final picture")
        win.scene.set_image(app.previous_picture)
        win.set_system_status(len(app.printer.get_all_tasks()), not app.printer.is_ready(),
                              app.count.printed, app.count.taken)
        self.print_view_timer.start(cfg.getfloat('PRINTER', 'printer_delay'))

    @pibooth.hookimpl
    def state_print_validate(self, app, win, events):
        printed = evts.find_event(events, evts.EVT_PIBOOTH_PRINT)
        self.forgotten = evts.find_event(events, evts.EVT_PIBOOTH_CAPTURE)
        if self.print_view_timer.is_timeout() or printed or self.forgotten:
            if printed:
                win.set_system_status(len(app.printer.get_all_tasks()), not app.printer.is_ready(),
                                      app.count.printed, app.count.taken)
            return 'finish'

    @pibooth.hookimpl
    def state_finish_enter(self, cfg, app, win):
        if cfg.getfloat('WINDOW', 'finish_picture_delay') > 0 and not self.forgotten:
            win.scene.set_image(app.previous_picture)
            timeout = cfg.getfloat('WINDOW', 'finish_picture_delay')
        else:
            win.scene.set_image(None)
            timeout = 1

        self.finish_timer.start(timeout)

    @pibooth.hookimpl
    def state_finish_validate(self):
        if self.finish_timer.is_timeout():
            return 'wait'
