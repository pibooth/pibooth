# -*- coding: utf-8 -*-

"""Pibooth utilities.
"""

import os
import sys
import time
import types
import os.path as osp
import logging
import psutil
import platform
import contextlib
import errno
import subprocess
from fnmatch import fnmatchcase
from itertools import zip_longest, islice
try:
    from pip._internal.operations import freeze
except ImportError:  # pip < 10.0
    from pip.operations import freeze

LOGGER = logging.getLogger("pibooth")
logging.getLogger("pip").setLevel(logging.WARNING)


class BlockConsoleHandler(logging.StreamHandler):

    default_level = logging.INFO
    pattern_start = '+<- '
    pattern_block = '|   '
    pattern_end = '+-> '
    current_indent = ''

    def emit(self, record):
        cls = self.__class__
        if cls.is_debug():
            record.msg = '{}{}'.format(cls.current_indent, record.msg)
        logging.StreamHandler.emit(self, record)

        if cls.current_indent.endswith(cls.pattern_start):
            cls.current_indent = (cls.current_indent[:-len(cls.pattern_start)] + cls.pattern_block)
        elif cls.current_indent.endswith(cls.pattern_end):
            cls.current_indent = cls.current_indent[:-len(cls.pattern_end)]

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
            cls.current_indent += cls.pattern_start

    @classmethod
    def dedent(cls):
        """End the current log block.
        """
        if cls.is_debug():
            cls.current_indent = (cls.current_indent[:-len(cls.pattern_block)] + cls.pattern_end)


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

    def is_started(self):
        """Return True if time is started.
        """
        return self.time is not None

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


def get_pkg_versions():
    """Return the list of Python packages and versions used by pibooth.
    """
    used_pkgs = []
    installed_pkgs = [pkg for pkg in freeze.freeze()]
    for name, val in sys.modules.items():
        if isinstance(val, types.ModuleType):
            found = [pkg for pkg in installed_pkgs if name in pkg]
            if found:
                for pkg in found:
                    if pkg.startswith("-e ") or pkg.startswith("# "):
                        pkg = pkg.rsplit("/")[-1].rsplit("#egg=")[-1] + "==dev"
                    used_pkgs.append(pkg)
    return set(used_pkgs)


def get_crash_message():
    """Format a message to give most information about environment.
    """
    msg = "system='{}', node='{}', release='{}', version='{}', machine='{}', processor='{}', ".format(*platform.uname())
    msg += ", ".join(get_pkg_versions()) + "\n"
    msg += " " + "*" * 83 + "\n"
    msg += " * " + "Oops! It seems that pibooth has crashed".center(80) + "*\n"
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
    """Open a text editor to edit a file.
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


def take(n, iterable):
    """Return first n items of the iterable as a list.
    """
    return list(islice(iterable, n))


def format_columns_words(words, column_count=3):
    """Return a list of words into columns.
    """
    lines = []
    columns, dangling = divmod(len(words), column_count)
    iter_words = iter(words)
    columns = [take(columns + (dangling > i), iter_words) for i in range(column_count)]
    paddings = [max(map(len, column)) for column in columns]
    for row in zip_longest(*columns, fillvalue=''):
        lines.append('  '.join(word.ljust(pad) for word, pad in zip(row, paddings)))
    return lines


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
        if hasattr(hook, 'find_spec'):
            spec = hook.find_spec(modname, [dirname])
            if spec:
                return spec.loader.load_module(modname)
        else:
            # Deprecated since Python 3.4
            loader = hook.find_module(modname, [dirname])
            if loader:
                return loader.load_module(modname)
    LOGGER.warning("Can not load Python module '%s' from '%s'", modname, path)
