# -*- coding: utf-8 -*-

import os
import os.path as osp
import itertools
from concurrent import futures
from datetime import datetime
import pibooth
from pibooth import evts
from pibooth.utils import LOGGER, PollingTimer
from pibooth.tasks import AsyncTask
from pibooth.pictures import get_picture_factory


def build_and_save(factory, savedirs, date, filename):
    for savedir in savedirs:
        rawdir = osp.join(savedir, "raw", date)
        os.makedirs(rawdir)

        for count, capture in enumerate(factory._images):
            capture.save(osp.join(rawdir, "pibooth{:03}.jpg".format(count)))

    LOGGER.info("Creating the final picture")
    factory.build()

    for savedir in savedirs:
        picture_path = osp.join(savedir, filename)
        factory.save(picture_path)
    return factory, picture_path


class PicturePlugin(object):

    """Plugin to build the final picture.
    """

    __name__ = 'pibooth-core:picture'

    def __init__(self, plugin_manager):
        self._pm = plugin_manager
        self.timer = PollingTimer()
        self.picture_worker = None
        self.factory_pool = futures.ProcessPoolExecutor()
        self.factory_pool_results = []
        self.second_previous_picture = None
        self.texts_vars = {}

    def _reset_vars(self, app):
        """Destroy final picture (can not be used anymore).
        """
        self.factory_pool_results = []
        app.previous_picture = None
        app.previous_animated = None
        app.previous_picture_file = None

    @pibooth.hookimpl(hookwrapper=True)
    def pibooth_setup_picture_factory(self, cfg, opt_index, factory):

        outcome = yield  # all corresponding hookimpls are invoked here
        factory = outcome.get_result() or factory

        nbr_capture_choices = len(cfg.gettuple('PICTURE', 'captures', int))
        factory.set_margin(cfg.getint('PICTURE', 'margin_thick'))

        backgrounds = cfg.gettuple('PICTURE', 'backgrounds', ('color', 'path'), nbr_capture_choices)
        factory.set_background(backgrounds[opt_index])

        overlays = cfg.gettuple('PICTURE', 'overlays', 'path', nbr_capture_choices)
        if overlays[opt_index]:
            factory.set_overlay(overlays[opt_index])

        texts = [cfg.get('PICTURE', 'footer_text1').strip('"').format(**self.texts_vars),
                 cfg.get('PICTURE', 'footer_text2').strip('"').format(**self.texts_vars)]
        colors = cfg.gettuple('PICTURE', 'text_colors', 'color', len(texts))
        text_fonts = cfg.gettuple('PICTURE', 'text_fonts', str, len(texts))
        alignments = cfg.gettuple('PICTURE', 'text_alignments', str, len(texts))
        if any(elem != '' for elem in texts):
            for params in zip(texts, text_fonts, colors, alignments):
                factory.add_text(*params)

        if cfg.getboolean('PICTURE', 'captures_cropping'):
            factory.set_cropping()

        if cfg.getboolean('GENERAL', 'debug'):
            factory.set_outlines()

        outcome.force_result(factory)

    @pibooth.hookimpl
    def pibooth_cleanup(self):
        self.factory_pool.shutdown(wait=True)

    @pibooth.hookimpl
    def state_failsafe_enter(self, app):
        self._reset_vars(app)

    @pibooth.hookimpl
    def state_wait_enter(self, cfg, app):
        animated = [fn.result() for fn in futures.wait(self.factory_pool_results).done]
        if cfg.getfloat('WINDOW', 'wait_picture_delay') == 0:
            # Do it here to avoid a transient display of the picture
            self._reset_vars(app)
        elif animated:
            app.previous_animated = itertools.cycle(animated)

        # Reset timeout in case of settings changed
        self.timer.start(max(0, cfg.getfloat('WINDOW', 'wait_picture_delay')))

    @pibooth.hookimpl
    def state_wait_do(self, cfg, app):
        if cfg.getfloat('WINDOW', 'wait_picture_delay') > 0 and self.timer.is_timeout()\
                and app.previous_picture_file:
            self._reset_vars(app)

    @pibooth.hookimpl
    def state_processing_enter(self, cfg, app):
        self.second_previous_picture = app.previous_picture
        self._reset_vars(app)

        idx = app.capture_choices.index(app.capture_nbr)
        self.texts_vars['date'] = datetime.strptime(app.capture_date, "%Y-%m-%d-%H-%M-%S")
        self.texts_vars['count'] = app.count

        LOGGER.info("Saving raw captures")
        captures = app.camera.grab_captures()
        default_factory = get_picture_factory(captures, cfg.get('PICTURE', 'orientation'))
        factory = self._pm.hook.pibooth_setup_picture_factory(cfg=cfg,
                                                              opt_index=idx,
                                                              factory=default_factory)
        self.picture_worker = AsyncTask(build_and_save,
                                        args=(factory,
                                              cfg.gettuple('GENERAL', 'directory', 'path'),
                                              app.capture_date,
                                              app.picture_filename))

    @pibooth.hookimpl
    def state_processing_do(self, app):
        if not self.picture_worker.is_alive():
            factory, app.previous_picture_file = self.picture_worker.result()
            app.previous_picture = factory.build()  # Get last generated picture

    @pibooth.hookimpl
    def state_processing_exit(self, cfg, app):
        app.count.taken += 1  # Do it here because 'print' state can be skipped
        idx = app.capture_choices.index(app.capture_nbr)

        if cfg.getboolean('WINDOW', 'animate') and app.capture_nbr > 1:
            LOGGER.info("Asyncronously generate pictures for animation")
            factory, _ = self.picture_worker.result()
            for capture in factory._images:
                default_factory = get_picture_factory((capture,), cfg.get(
                    'PICTURE', 'orientation'), force_pil=True, dpi=200)
                factory = self._pm.hook.pibooth_setup_picture_factory(cfg=cfg,
                                                                      opt_index=idx,
                                                                      factory=default_factory)
                factory.set_margin(factory._margin // 3)  # 1/3 since DPI is divided by 3
                self.factory_pool_results.append(self.factory_pool.submit(factory.build))

    @pibooth.hookimpl
    def state_print_do(self, cfg, app, events):
        if evts.find_event(events, evts.EVT_PIBOOTH_CAPTURE):

            LOGGER.info("Moving the picture in the forget folder")
            for savedir in cfg.gettuple('GENERAL', 'directory', 'path'):
                forgetdir = osp.join(savedir, "forget")
                if not osp.isdir(forgetdir):
                    os.makedirs(forgetdir)
                os.rename(osp.join(savedir, app.picture_filename), osp.join(forgetdir, app.picture_filename))

            self._reset_vars(app)
            app.count.forgotten += 1
            app.previous_picture = self.second_previous_picture

            # Deactivate the print function for the backuped picture
            # as we don't known how many times it has already been printed
            app.count.remaining_duplicates = 0
