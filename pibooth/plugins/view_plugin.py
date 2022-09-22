# -*- coding: utf-8 -*-

import pibooth
from pibooth import evtfilters
from pibooth.utils import LOGGER, get_crash_message, PollingTimer


class ViewPlugin(object):

    """Plugin to manage the pibooth window dans transitions.
    """

    __name__ = 'pibooth-core:view'

    def __init__(self, plugin_manager):
        self._pm = plugin_manager
        self.count = 0
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

        win.set_image(previous_picture)
        win.scene.update_print_action(app.previous_picture and app.printer.is_ready()
                                      and app.count.remaining_duplicates > 0)
        if app.printer.is_installed():
            win.set_print_number(len(app.printer.get_all_tasks()), not app.printer.is_ready())

    @pibooth.hookimpl
    def state_wait_do(self, app, win, events):
        if app.previous_animated and self.animated_frame_timer.is_timeout():
            win.scene.update_print_action(app.printer.is_ready() and app.count.remaining_duplicates > 0)
            self.animated_frame_timer.start()
            win.set_image(next(app.previous_animated))

        if evtfilters.find_event(events, evtfilters.EVT_PRINTER_TASKS_UPDATED) and app.printer.is_installed():
            win.set_print_number(len(app.printer.get_all_tasks()), not app.printer.is_ready())

        if evtfilters.find_event(events, evtfilters.EVT_PIBOOTH_BTN_PRINT):
            win.scene.update_print_action(app.printer.is_ready() and app.count.remaining_duplicates > 0)

    @pibooth.hookimpl
    def state_wait_validate(self, cfg, app, events):
        if evtfilters.find_event(events, evtfilters.EVT_PIBOOTH_BTN_CAPTURE):
            if len(app.capture_choices) > 1:
                return 'choose'
            if cfg.getfloat('WINDOW', 'chosen_delay') > 0:
                return 'chosen'
            return 'preview'

    @pibooth.hookimpl
    def state_wait_exit(self):
        self.count = 0

    @pibooth.hookimpl
    def state_choose_enter(self, app, win):
        LOGGER.info("Show picture choice (nothing selected)")
        win.set_print_number(0, False)  # Hide printer status
        win.scene.set_choices(app.capture_choices)
        self.choose_timer.start()

    @pibooth.hookimpl
    def state_choose_do(self, app, win, events):
        if evtfilters.find_event(events, evtfilters.EVT_PIBOOTH_BTN_CAPTURE):
            app.capture_nbr = win.scene.get_selection()
        if evtfilters.find_event(events, evtfilters.EVT_PIBOOTH_BTN_PRINT):
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
        self.count += 1
        self.capture_finished = False
        win.scene.set_capture_number(self.count, app.capture_nbr)

    @pibooth.hookimpl
    def state_preview_do(self, win, events):
        for event in events:
            if event.type == evtfilters.EVT_PIBOOTH_CAM_PREVIEW:
                win.set_image(event.result)

    @pibooth.hookimpl
    def state_capture_enter(self, cfg, app, win):
        if cfg.getboolean('WINDOW', 'flash'):
            win.scene.trigger_flash()
        win.scene.set_capture_number(self.count, app.capture_nbr)

    @pibooth.hookimpl
    def state_capture_do(self, events):
        if evtfilters.find_event(events, evtfilters.EVT_PIBOOTH_CAM_CAPTURE):
            self.capture_finished = True

    @pibooth.hookimpl
    def state_capture_validate(self, cfg, app, win):
        if self.capture_finished and (not cfg.getboolean('WINDOW', 'flash') or win.scene.count_flash >= 3):
            if self.count >= app.capture_nbr:
                return 'processing'
            return 'preview'

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
        win.set_image(app.previous_picture)
        win.set_print_number(len(app.printer.get_all_tasks()), not app.printer.is_ready())
        self.print_view_timer.start(cfg.getfloat('PRINTER', 'printer_delay'))

    @pibooth.hookimpl
    def state_print_validate(self, app, win, events):
        printed = evtfilters.find_event(events, evtfilters.EVT_PIBOOTH_BTN_PRINT)
        self.forgotten = evtfilters.find_event(events, evtfilters.EVT_PIBOOTH_BTN_CAPTURE)
        if self.print_view_timer.is_timeout() or printed or self.forgotten:
            if printed:
                win.set_print_number(len(app.printer.get_all_tasks()), not app.printer.is_ready())
            return 'finish'

    @pibooth.hookimpl
    def state_finish_enter(self, cfg, app, win):
        if cfg.getfloat('WINDOW', 'finish_picture_delay') > 0 and not self.forgotten:
            win.set_image(app.previous_picture)
            timeout = cfg.getfloat('WINDOW', 'finish_picture_delay')
        else:
            win.set_image()
            timeout = 1

        self.finish_timer.start(timeout)

    @pibooth.hookimpl
    def state_finish_validate(self):
        if self.finish_timer.is_timeout():
            return 'wait'
