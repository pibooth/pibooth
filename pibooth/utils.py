# -*- coding: utf-8 -*-

import time
import logging
import contextlib

LOGGER = logging.getLogger("pibooth")


@contextlib.contextmanager
def timeit(description):
    LOGGER.info(description)
    start = time.time()
    try:
        yield
    finally:
        LOGGER.debug("    -> took %0.3f seconds.", time.time() - start)


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
