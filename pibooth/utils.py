# -*- coding: utf-8 -*-

"""Pibooth utilities.
"""

import os
import sys
import time
import os.path as osp
import logging
import threading
import psutil
import platform
from fnmatch import fnmatchcase
import contextlib
import errno
import subprocess
from concurrent import futures
import pygame
from pibooth import evtfilters

LOGGER = logging.getLogger("pibooth")


class AsyncTask(object):

    POOL = futures.ThreadPoolExecutor()
    FUTURES = {}

    def __init__(self, runnable, args=(), event=None, loop=False):
        self._stop_event = threading.Event()
        self.runnable = runnable
        self.event_type = event
        self.loop = loop
        self.future = self.POOL.submit(self._run, *args)
        self.FUTURES[self.future] = self
        self.future.add_done_callback(self._finish)

    def _finish(self, future):
        """Remove future from tracking list.
        """
        self.FUTURES.pop(future)
        self.future.result()  # Raise exception is occures during run

    def _run(self, *args, **kwargs):
        """Execute the runnable.
        """
        result = None
        while not self._stop_event.is_set():
            result = self.runnable(*args, **kwargs)
            self.emit(result)
            if not self.loop:
                break
        return result

    def emit(self, data):
        """Post event with the result of the task.
        """
        if self.event_type is not None:
            event = pygame.event.Event(self.event_type, result=data)
            evtfilters.post(event)

    def result(self):
        """Return task result.
        """
        return self.future.result()

    def is_alive(self):
        """Return true if the task is not yet started or running.
        """
        return not self.future.done()

    def wait(self, timeout=None):
        """Wait for task ends or cancelled.
        """
        try:
            return self.future.result(timeout)
        except futures.TimeoutError:
            raise
        except Exception:
            return None

    def kill(self):
        """Stop running.
        """
        self._stop_event.set()
        self.future.cancel()
        self.wait()

    @classmethod
    def kill_all(cls):
        """Stop all tasks and don't accept new one.
        """
        for task in cls.FUTURES.values():
            task.kill()
        cls.FUTURES.clear()
        cls.POOL.shutdown(wait=True)


class BlockConsoleHandler(logging.StreamHandler):

    default_level = logging.INFO
    pattern_indent = '+< '
    pattern_blocks = '|  '
    pattern_dedent = '+> '
    current_indent = ''

    def emit(self, record):
        cls = self.__class__
        if cls.is_debug():
            record.msg = '{}{}'.format(cls.current_indent, record.msg)
        logging.StreamHandler.emit(self, record)

        if cls.current_indent.endswith(cls.pattern_indent):
            cls.current_indent = (cls.current_indent[:-len(cls.pattern_indent)] + cls.pattern_blocks)
        elif cls.current_indent.endswith(cls.pattern_dedent):
            cls.current_indent = cls.current_indent[:-len(cls.pattern_dedent)]

    @classmethod
    def is_debug(cls):
        """Return True if this handler is set to DEBUG level on the root logger.
        """
        for hdlr in logging.getLogger().handlers:
            if isinstance(hdlr, cls):
                return hdlr.level < logging.INFO
        return False

    @classmethod
    def indent(cls):
        """Begin a new log block.
        """
        if cls.is_debug():
            cls.current_indent += cls.pattern_indent

    @classmethod
    def dedent(cls):
        """End the current log block.
        """
        if cls.is_debug():
            cls.current_indent = (cls.current_indent[:-len(cls.pattern_blocks)] + cls.pattern_dedent)


class PollingTimer(object):

    """
    Timer to be used in a pooling loop to check if timeout has been exceed.
    """

    def __init__(self, timeout=0, start=True):
        self.timeout = timeout
        self.time = None
        self._paused_total = 0
        self._paused_time = None
        if start:
            self.start()

    def __enter__(self):
        """Start timer if used as context manager.
        """
        self.start()
        return self

    def __exit__(self, *args):
        """Stop timer if used as context manager.
        """
        self.time = None

    def reset(self):
        """Reset timer to its initial state.
        """
        self.time = None
        self._paused_total = 0
        self._paused_time = None

    def start(self, timeout=None):
        """Start the timer.
        """
        if timeout is not None:
            self.timeout = timeout
            self._paused_time = None
        if self.timeout < 0:
            raise ValueError("PollingTimer cannot be started if timeout is lower than zero")
        if self._paused_time:
            self._paused_total += time.time() - self._paused_time
            self._paused_time = None
        else:
            self._paused_total = 0
            self.time = time.time()

    def freeze(self):
        """Pause the timer.
        """
        if not self._paused_time:
            self._paused_time = time.time()

    def remaining(self):
        """Return the remaining seconds.
        """
        if self.time is None:
            remain = float(self.timeout)
        else:
            remain = self.timeout + self.paused() - (time.time() - self.time)
            if remain < 0.0:
                remain = 0.0
        return remain

    def paused(self):
        """Return the pause duration in seconds.
        """
        if self._paused_time:
            return self._paused_total + time.time() - self._paused_time
        return self._paused_total

    def elapsed(self):
        """Return the elapsed seconds.
        """
        if self.time is None:
            return 0.0
        return time.time() - self.time - self.paused()

    def is_timeout(self):
        """Return True if the timer is in timeout.
        """
        if self.time is None:
            raise RuntimeError("PollingTimer has never been started")
        return (time.time() - self.time - self.paused()) > self.timeout


def configure_logging(level=logging.INFO, msgfmt=logging.BASIC_FORMAT, datefmt=None, filename=None):
    """Configure root logger for console printing.
    """
    root = logging.getLogger()

    if not root.handlers:
        # Set lower level to be sure that all handlers receive the logs
        root.setLevel(logging.DEBUG)

        if filename:
            # Create a file handler, all levels are logged
            filename = osp.abspath(osp.expanduser(filename))
            dirname = osp.dirname(filename)
            if not osp.isdir(dirname):
                os.makedirs(dirname)
            hdlr = logging.FileHandler(filename, mode='w')
            hdlr.setFormatter(logging.Formatter(msgfmt, datefmt))
            hdlr.setLevel(logging.DEBUG)
            root.addHandler(hdlr)

        # Create a console handler
        hdlr = BlockConsoleHandler(sys.stdout)
        hdlr.setFormatter(logging.Formatter(msgfmt, datefmt))
        if level is not None:
            hdlr.setLevel(level)
            BlockConsoleHandler.default_level = level
        root.addHandler(hdlr)


def set_logging_level(level=None):
    """Set/restore the log level of the concole.

    :param level: level as defined in the logging package
    :type level: int
    """
    for hdlr in logging.getLogger().handlers:
        if isinstance(hdlr, BlockConsoleHandler):
            if level is None:
                # Restore the default level
                level = BlockConsoleHandler.default_level
            hdlr.setLevel(level)


def get_logging_filename():
    """Return the absolute path to the logs filename if set.
    """
    for hdlr in logging.getLogger().handlers:
        if isinstance(hdlr, logging.FileHandler):
            return hdlr.baseFilename
    return None


def get_crash_message():
    msg = "system='{}', node='{}', release='{}', version='{}', machine='{}', processor='{}'\n".format(*platform.uname())
    msg += " " + "*" * 83 + "\n"
    msg += " * " + "Oops! It seems that pibooth has crached".center(80) + "*\n"
    msg += " * " + "You can report an issue on https://github.com/pibooth/pibooth/issues/new".center(80) + "*\n"
    if get_logging_filename():
        msg += " * " + ("and post the file: {}".format(get_logging_filename())).center(80) + "*\n"
    msg += " " + "*" * 83
    return msg


@contextlib.contextmanager
def timeit(description):
    """Measure time execution.
    """
    BlockConsoleHandler.indent()
    LOGGER.info(description)
    start = time.time()
    try:
        yield
    finally:
        BlockConsoleHandler.dedent()
        LOGGER.debug("took %0.3f seconds", time.time() - start)


def pkill(pattern):
    """Kill all process matching the given pattern.

    :param pattern: pattern used to match processes
    :type pattern: str
    """
    for proc in psutil.process_iter():
        if fnmatchcase(proc.name(), pattern):
            LOGGER.debug("Try to kill process '%s'", proc.name())
            try:
                proc.kill()
            except psutil.AccessDenied:
                raise EnvironmentError("Can not kill '{}', root access is required. "
                                       "(kill it manually before starting pibooth)".format(proc.name()))


def open_text_editor(filename):
    """Open a text editor to edit the configuration file.
    """
    editors = ['leafpad', 'mousepad', 'vi', 'emacs']
    for editor in editors:
        try:
            process = subprocess.Popen([editor, filename])
            process.communicate()
            return True
        except OSError as e:
            if e.errno != errno.ENOENT:
                # Something else went wrong while trying to run the editor
                raise
    LOGGER.critical("Can't find installed text editor among %s", editors)
    return False


def load_module(path):
    """Load a Python module dynamically.
    """
    if not osp.isfile(path):
        raise ValueError("Invalid Python module path '{}'".format(path))

    dirname, filename = osp.split(path)
    modname = osp.splitext(filename)[0]

    if dirname not in sys.path:
        sys.path.append(dirname)

    for hook in sys.meta_path:
        if hasattr(hook, 'find_module'):
            # Deprecated since Python 3.4
            loader = hook.find_module(modname, [dirname])
            if loader:
                return loader.load_module(modname)
        else:
            spec = hook.find_spec(modname, [dirname])
            if spec:
                return spec.loader.load_module(modname)

    LOGGER.warning("Can not load Python module '%s' from '%s'", modname, path)
