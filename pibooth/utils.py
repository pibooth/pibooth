# -*- coding: utf-8 -*-

import sys
import time
import logging
import contextlib


LOGGER = logging.getLogger("pibooth")


class BlockConsoleHandler(logging.StreamHandler):

    pattern_indent = '+< '
    pattern_blocks = '|  '
    pattern_dedent = '+> '
    current_indent = ''

    def emit(self, record):
        cls = self.__class__
        record.msg = '{}{}'.format(cls.current_indent, record.msg)
        logging.StreamHandler.emit(self, record)

        if cls.current_indent.endswith(cls.pattern_indent):
            cls.current_indent = (cls.current_indent[:-len(cls.pattern_indent)] + cls.pattern_blocks)
        elif cls.current_indent.endswith(cls.pattern_dedent):
            cls.current_indent = cls.current_indent[:-len(cls.pattern_dedent)]

    @classmethod
    def indent(cls):
        """Begin a new log block.
        """
        cls.current_indent += cls.pattern_indent

    @classmethod
    def dedent(cls):
        """End the current log block.
        """
        cls.current_indent = (cls.current_indent[:-len(cls.pattern_blocks)] + cls.pattern_dedent)


def configure_logging(level=logging.INFO, msgfmt=logging.BASIC_FORMAT, datefmt=None):
    """Configure root logger for console printing.
    """
    root = logging.getLogger()
    if not root.handlers:
        hdlr = BlockConsoleHandler(sys.stdout)
        hdlr.setFormatter(logging.Formatter(msgfmt, datefmt))
        root.addHandler(hdlr)
        if level is not None:
            root.setLevel(level)


@contextlib.contextmanager
def timeit(description):
    """Measure time execution.
    """
    if LOGGER.getEffectiveLevel() < logging.INFO:
        BlockConsoleHandler.indent()
    LOGGER.info(description)
    start = time.time()
    try:
        yield
    finally:
        if LOGGER.getEffectiveLevel() < logging.INFO:
            BlockConsoleHandler.dedent()
        LOGGER.debug("took %0.3f seconds", time.time() - start)


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
        self.time = time.time()

    def remaining(self):
        """Return the remaining seconds.
        """
        if self.time is None:
            remain = float(self.timeout)
        else:
            remain = self.timeout - (time.time() - self.time)
            if remain < 0.0:
                remain = 0.0
        return remain

    def elapsed(self):
        """Return the elapsed seconds.
        """
        if self.time is None:
            return 0.0
        else:
            return time.time() - self.time

    def is_timeout(self):
        """Return True if the timer is in timeout.
        """
        if self.time is None:
            raise RuntimeError("PoolingTimer has never been started")
        else:
            return (time.time() - self.time) > self.timeout
