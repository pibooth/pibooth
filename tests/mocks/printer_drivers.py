# -*- coding: utf-8 -*-

"""Fake CUPS objects to test the printer without a CUPS server.
"""

from pibooth.printer import PRINTER_STATE_IDLE


class CupsConnectionMock:

    """Fake ``cups.Connection``.
    """

    def __init__(self, printers=None, default=None):
        self.printers = printers if printers is not None else {}
        self.default = default
        self.jobs = {}
        self.printed_files = []
        self._job_id = 0

    def getDefault(self):
        return self.default

    def getPrinters(self):
        return self.printers

    def enablePrinter(self, name):
        self.printers[name]['printer-state'] = PRINTER_STATE_IDLE
        self.printers[name]['printer-state-reasons'] = []

    def printFile(self, name, filename, title, options):
        self._job_id += 1
        self.jobs[self._job_id] = {'job-id': self._job_id, 'job-name': title, 'job-state': 3}
        self.printed_files.append((name, filename, options))
        return self._job_id

    def cancelAllJobs(self, name):
        self.jobs.clear()

    def getJobs(self, my_jobs=True, requested_attributes=None):
        return self.jobs


class CupsSubscriberMock:

    """Fake ``cups_notify.Subscriber``.
    """

    def __init__(self, conn):
        self.conn = conn
        self.callbacks = {}

    def is_subscribed(self, callback):
        return callback in self.callbacks

    def subscribe(self, callback, events):
        self.callbacks[callback] = events

    def unsubscribe_all(self):
        self.callbacks.clear()


class CupsEventMock:

    """Fake ``cups_notify.event`` module.
    """

    CUPS_EVT_JOB_COMPLETED = 'job-completed'
    CUPS_EVT_JOB_CREATED = 'job-created'
    CUPS_EVT_JOB_STOPPED = 'job-stopped'
    CUPS_EVT_PRINTER_STATE_CHANGED = 'printer-state-changed'
    CUPS_EVT_PRINTER_STOPPED = 'printer-stopped'


class CupsModuleMock:

    """Fake ``cups`` module.
    """

    def __init__(self, conn):
        self._conn = conn

    def Connection(self):
        return self._conn
