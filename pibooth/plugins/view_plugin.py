# -*- coding: utf-8 -*-

import pibooth
from pibooth import camera, pgevents
from pibooth.utils import LOGGER, get_crash_message, PollingTimer


class ViewPlugin(object):

    """Plugin to manage the pibooth window dans transitions.
    """

    def __init__(self, plugin_manager):
        self._pm = plugin_manager
        self.count = 0
        self.count_flash = 0
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
        # Seconds between each flash
        self.flash_timer = PollingTimer(0.05)
        # Seconds to display the selected layout
        self.print_view_timer = PollingTimer(0)
        # Seconds to display the selected layout
        self.finish_timer = PollingTimer(1)

    @pibooth.hookimpl
    def state_failsafe_enter(self, win):
        win.show_oops()
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

        win.show_intro(previous_picture, app.printer.is_ready()
                       and app.count.remaining_duplicates > 0)
        if app.printer.is_installed():
            win.set_print_number(len(app.printer.get_all_tasks()), not app.printer.is_ready())

    @pibooth.hookimpl
    def state_wait_do(self, app, win, events):
        if app.previous_animated and self.animated_frame_timer.is_timeout():
            previous_picture = next(app.previous_animated)
            win.show_intro(previous_picture, app.printer.is_ready()
                           and app.count.remaining_duplicates > 0)
            self.animated_frame_timer.start()
        else:
            previous_picture = app.previous_picture

        event = pgevents.find_print_status_event(events)
        if event and app.printer.is_installed():
            win.set_print_number(len(event.tasks), not app.printer.is_ready())

        if pgevents.find_print_event(events, win) or (win.get_image() and not previous_picture):
            win.show_intro(previous_picture, app.printer.is_ready()
                           and app.count.remaining_duplicates > 0)

    @pibooth.hookimpl
    def state_wait_validate(self, cfg, app, win, events):
        if pgevents.find_capture_event(events, win):
            if len(app.capture_choices) > 1:
                return 'choose'
            if cfg.getfloat('WINDOW', 'chosen_delay') > 0:
                return 'chosen'
            return 'preview'

    @pibooth.hookimpl
    def state_wait_exit(self, win):
        self.count = 0
        win.show_image(None)  # Clear currently displayed image

    @pibooth.hookimpl
    def state_choose_enter(self, app, win):
        LOGGER.info("Show picture choice (nothing selected)")
        win.set_print_number(0, False)  # Hide printer status
        win.show_choice(app.capture_choices)
        self.choose_timer.start()

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
        win.show_choice(app.capture_choices, selected=app.capture_nbr)
        self.layout_timer.start(cfg.getfloat('WINDOW', 'chosen_delay'))

    @pibooth.hookimpl
    def state_chosen_validate(self):
        if self.layout_timer.is_timeout():
            return 'preview'

    @pibooth.hookimpl
    def state_preview_enter(self, app, win):
        self.count += 1
        self.capture_finished = False
        win.set_capture_number(self.count, app.capture_nbr)

    @pibooth.hookimpl
    def state_preview_do(self, win, events):
        for event in events:
            if event.type == pgevents.EVT_CAMERA_PREVIEW:
                win.show_image(event.result)

    @pibooth.hookimpl
    def state_capture_enter(self):
        self.count_flash = 0
        self.flash_timer.start()

    @pibooth.hookimpl
    def state_capture_do(self, cfg, app, win, events):
        if cfg.getboolean('WINDOW', 'flash'):
            if self.flash_timer.is_timeout():
                self.count_flash += 1
                win.toggle_flash()
                self.flash_timer.start()

        win.set_capture_number(self.count, app.capture_nbr)

        for event in events:
            if event.type == pgevents.EVT_CAMERA_CAPTURE:
                self.capture_finished = True

    @pibooth.hookimpl
    def state_capture_validate(self, cfg, app):
        if self.capture_finished and (not cfg.getboolean('WINDOW', 'flash') or self.count_flash >= 4):
            if self.count >= app.capture_nbr:
                return 'processing'
            return 'preview'

    @pibooth.hookimpl
    def state_processing_enter(self, win):
        win.show_work_in_progress()

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
        win.show_print(app.previous_picture)
        win.set_print_number(len(app.printer.get_all_tasks()), not app.printer.is_ready())
        self.print_view_timer.start(cfg.getfloat('PRINTER', 'printer_delay'))

    @pibooth.hookimpl
    def state_print_validate(self, app, win, events):
        printed = pgevents.find_print_event(events, win)
        self.forgotten = pgevents.find_capture_event(events, win)
        if self.print_view_timer.is_timeout() or printed or self.forgotten:
            if printed:
                win.set_print_number(len(app.printer.get_all_tasks()), not app.printer.is_ready())
            return 'finish'

    @pibooth.hookimpl
    def state_finish_enter(self, cfg, app, win):
        if cfg.getfloat('WINDOW', 'finish_picture_delay') > 0 and not self.forgotten:
            win.show_finished(app.previous_picture)
            timeout = cfg.getfloat('WINDOW', 'finish_picture_delay')
        else:
            win.show_finished()
            timeout = 1

        self.finish_timer.start(timeout)

    @pibooth.hookimpl
    def state_finish_validate(self):
        if self.finish_timer.is_timeout():
            return 'wait'
