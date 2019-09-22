# -*- coding: utf-8 -*-

"""Pibooth utilities.
"""

import os
import sys
import time
import os.path as osp
import logging
import psutil
import functools
from fnmatch import fnmatchcase
import contextlib
try:
    from itertools import zip_longest, islice
except ImportError:
    # Python 2.x fallback
    from itertools import izip_longest as zip_longest, islice


LOGGER = logging.getLogger("pibooth")


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


class PoolingTimer(object):

    """
    Timer to be used in a pooling loop to check if timeout has been exceed.
    """

    def __init__(self, timeout, start=True):
        if timeout < 0:
            raise ValueError("PoolingTimer timeout can not be lower than zero")
        else:
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

    def start(self):
        """Start the timer.
        """
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
            raise RuntimeError("PoolingTimer has never been started")
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
            hdlr = logging.FileHandler(filename)
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


def set_logging_level(level=BlockConsoleHandler.default_level):
    """Set/restore the log level of the concole.
    """
    for hdlr in logging.getLogger().handlers:
        if isinstance(hdlr, BlockConsoleHandler):
            hdlr.setLevel(level)


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


def take(n, iterable):
    """Return first n items of the iterable as a list.
    """
    return list(islice(iterable, n))


def print_columns_words(words, column_count=3):
    """Print a list of words into columns.
    """
    columns, dangling = divmod(len(words), column_count)
    iter_words = iter(words)
    columns = [take(columns + (dangling > i), iter_words) for i in range(column_count)]
    paddings = [max(map(len, column)) for column in columns]
    for row in zip_longest(*columns, fillvalue=''):
        print('  '.join(word.ljust(pad) for word, pad in zip(row, paddings)))


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


def memorize(func):
    """Decorator to memorize and return the latest result
    of a function.
    """
    cache = {}

    @functools.wraps(func)
    def memorized_func_wrapper(*args, **kwargs):
        if func not in cache:
            cache[func] = func(*args, **kwargs)
        return cache[func]

    return memorized_func_wrapper
