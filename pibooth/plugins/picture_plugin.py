# -*- coding: utf-8 -*-

import os
import os.path as osp
import itertools
import pibooth
from pibooth.utils import timeit, PoolingTimer
from pibooth.pictures import get_picture_factory
from pibooth.pictures.pool import PicturesFactoryPool


class PicturePlugin(object):

    """Plugin to build the final picture.
    """

    def __init__(self):
        self.factory_pool = PicturesFactoryPool()
        self.picture_destroy_timer = PoolingTimer(0)
        self.second_previous_picture = None

    def _reset_vars(self, app):
        """Destroy final picture (can not be used anymore).
        """
        self.factory_pool.clear()
        app.previous_picture = None
        app.previous_animated = None
        app.previous_picture_file = None

    @pibooth.hookimpl
    def pibooth_setup_picture_factory(self, cfg, opt_index, factory):
        backgrounds = cfg.gettuple('PICTURE', 'backgrounds', ('color', 'path'), 2)
        factory.set_background(backgrounds[opt_index])

        overlays = cfg.gettuple('PICTURE', 'overlays', 'path', 2)
        if overlays[opt_index]:
            factory.set_overlay(overlays[opt_index])

        texts = [cfg.get('PICTURE', 'footer_text1').strip('"'),
                 cfg.get('PICTURE', 'footer_text2').strip('"')]
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

    @pibooth.hookimpl
    def pibooth_cleanup(self):
        self.factory_pool.quit()

    @pibooth.hookimpl
    def state_failsafe_enter(self, app):
        self._reset_vars(app)

    @pibooth.hookimpl
    def state_wait_enter(self, cfg, app):
        animated = self.factory_pool.get()
        if animated:
            app.previous_animated = itertools.cycle(animated)

        # Reset timeout in case of settings changed
        self.picture_destroy_timer.timeout = max(0, cfg.getfloat('WINDOW', 'final_image_delay'))
        self.picture_destroy_timer.start()

    @pibooth.hookimpl
    def state_wait_do(self, cfg, app):
        if cfg.getfloat('WINDOW', 'final_image_delay') > 0 and self.picture_destroy_timer.is_timeout():
            self._reset_vars(app)

    @pibooth.hookimpl
    def state_processing_enter(self, app):
        self.second_previous_picture = app.previous_picture
        self._reset_vars(app)

    @pibooth.hookimpl
    def state_processing_do(self, cfg, app):
        idx = app.capture_choices.index(app.capture_nbr)

        with timeit("Creating the final picture"):
            captures = app.camera.get_captures()
            factory = get_picture_factory(captures, cfg.get('PICTURE', 'orientation'))
            app._plugin_manager.hook.pibooth_setup_picture_factory(cfg=cfg,
                                                                   opt_index=idx,
                                                                   factory=factory)
            app.previous_picture = factory.build()

        savedir = cfg.getpath('GENERAL', 'directory')
        app.previous_picture_file = osp.join(savedir, osp.basename(app.dirname) + "_pibooth.jpg")
        factory.save(app.previous_picture_file)

        if cfg.getboolean('WINDOW', 'animate') and app.capture_nbr > 1:
            with timeit("Asyncronously generate pictures for animation"):
                for capture in captures:
                    factory = get_picture_factory((capture,), cfg.get('PICTURE', 'orientation'), force_pil=True)
                    app._plugin_manager.hook.pibooth_setup_picture_factory(cfg=cfg,
                                                                           opt_index=idx,
                                                                           factory=factory)
                    self.factory_pool.add(factory)

    @pibooth.hookimpl
    def state_print_do(self, cfg, app, events):
        if app.find_capture_event(events):
            with timeit("Putting the capture in the forget folder"):
                file_dir, file_name = osp.split(app.previous_picture_file)
                forget_dir = osp.join(file_dir, "forget")
                if not os.path.exists(forget_dir):
                    os.makedirs(forget_dir)
                os.rename(app.previous_picture_file, osp.join(forget_dir, file_name))
                self._reset_vars(app)
                app.previous_picture = self.second_previous_picture
                app.nbr_duplicates = cfg.getint('PRINTER', 'max_duplicates') + 1
