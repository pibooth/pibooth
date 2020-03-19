# -*- coding: utf-8 -*-

import itertools
import pibooth
from pibooth.utils import timeit, PoolingTimer


class ViewPlugin(object):

    """Plugin to manage the pibooth window dans transitions.
    """

    def __init__(self):
        self.count = 0
        # Seconds to display the failed message
        self.failed_view_timer = PoolingTimer(2)
        # Seconds between each animated frame
        self.animated_frame_timer = PoolingTimer(0)
        # Seconds before going back to the start
        self.choose_timer = PoolingTimer(30)
        # Seconds to display the selected layout
        self.layout_timer = PoolingTimer(4)
        # Seconds to display the selected layout
        self.print_view_timer = PoolingTimer(0)
        # Seconds to display the selected layout
        self.finish_timer = PoolingTimer(0.5)

    @pibooth.hookimpl
    def state_failsafe_enter(self, app):
        app.window.show_oops()
        self.failed_view_timer.start()

    @pibooth.hookimpl
    def state_failsafe_validate(self):
        if self.failed_view_timer.is_timeout():
            return 'wait'

    @pibooth.hookimpl
    def state_wait_enter(self, cfg, app):
        animated = app.makers_pool.get()

        if cfg.getboolean('WINDOW', 'animate') and animated:
            app.previous_animated = itertools.cycle(animated)
            previous_picture = next(app.previous_animated)

            # Reset timeout in case of settings changed
            self.animated_frame_timer.timeout = cfg.getfloat('WINDOW', 'animate_delay')
            self.animated_frame_timer.start()
        else:
            previous_picture = app.previous_picture

        app.window.show_intro(previous_picture, app.printer.is_installed() and
                              app.nbr_duplicates < cfg.getint('PRINTER', 'max_duplicates') and
                              not app.printer_unavailable)
        app.window.set_print_number(len(app.printer.get_all_tasks()), app.printer_unavailable)

    @pibooth.hookimpl
    def state_wait_do(self, cfg, app, events):

        if cfg.getboolean('WINDOW', 'animate') and app.previous_animated and self.animated_frame_timer.is_timeout():
            previous_picture = next(app.previous_animated)
            app.window.show_intro(previous_picture, app.printer.is_installed() and
                                  app.nbr_duplicates < cfg.getint('PRINTER', 'max_duplicates') and
                                  not app.printer_unavailable)
            self.animated_frame_timer.start()
        else:
            previous_picture = app.previous_picture

        event = app.find_print_status_event(events)
        if event:
            app.window.set_print_number(len(event.tasks), app.printer_unavailable)

        if not previous_picture:
            app.window.show_intro(None, False)

    @pibooth.hookimpl
    def state_wait_validate(self, app, events):
        if app.find_capture_event(events):
            if len(app.capture_choices) > 1:
                return 'choose'
            return 'preview'  # No choice

    @pibooth.hookimpl
    def state_wait_exit(self, app):
        self.count = 0
        app.window.show_image(None)  # Clear currently displayed image

    @pibooth.hookimpl
    def state_choose_enter(self, app):
        with timeit("Show picture choice (nothing selected)"):
            app.window.set_print_number(0)  # Hide printer status
            app.window.show_choice(app.capture_choices)
        self.choose_timer.start()

    @pibooth.hookimpl
    def state_choose_validate(self, app):
        if app.capture_nbr:
            return 'chosen'
        elif self.choose_timer.is_timeout():
            return 'wait'

    @pibooth.hookimpl
    def state_chosen_enter(self, app):
        with timeit("Show picture choice ({} captures selected)".format(app.capture_nbr)):
            app.window.show_choice(app.capture_choices, selected=app.capture_nbr)
        self.layout_timer.start()

    @pibooth.hookimpl
    def state_chosen_validate(self):
        if self.layout_timer.is_timeout():
            return 'preview'

    @pibooth.hookimpl
    def state_preview_enter(self, app):
        self.count += 1
        app.window.set_capture_number(self.count, app.capture_nbr)

    @pibooth.hookimpl
    def state_preview_validate(self):
        return 'capture'

    @pibooth.hookimpl
    def state_capture_do(self, app):
        app.window.set_capture_number(self.count, app.capture_nbr)

    @pibooth.hookimpl
    def state_capture_validate(self, app):
        if self.count >= app.capture_nbr:
            return 'processing'
        return 'preview'

    @pibooth.hookimpl
    def state_processing_enter(self, app):
        app.window.show_work_in_progress()

    @pibooth.hookimpl
    def state_processing_validate(self, cfg, app):
        if app.printer.is_installed() and cfg.getfloat('PRINTER', 'printer_delay') > 0 \
                and not app.printer_unavailable:
            return 'print'
        else:
            return 'finish'  # Can not print

    @pibooth.hookimpl
    def state_print_enter(self, cfg, app):
        with timeit("Display the final picture"):
            app.window.set_print_number(len(app.printer.get_all_tasks()), app.printer_unavailable)
            app.window.show_print(app.previous_picture)

        # Reset timeout in case of settings changed
        self.print_view_timer.timeout = cfg.getfloat('PRINTER', 'printer_delay')
        self.print_view_timer.start()

    @pibooth.hookimpl
    def state_print_validate(self, app, events):
        printed = app.find_print_event(events)
        forgotten = app.find_capture_event(events)
        if self.print_view_timer.is_timeout() or printed or forgotten:
            if printed:
                app.window.set_print_number(len(app.printer.get_all_tasks()), app.printer_unavailable)
            return 'finish'

    @pibooth.hookimpl
    def state_finish_enter(self, app):
        app.window.show_finished()
        self.finish_timer.start()

    @pibooth.hookimpl
    def state_finish_validate(self):
        if self.finish_timer.is_timeout():
            return 'wait'
