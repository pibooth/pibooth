# -*- coding: utf-8 -*-

"""Fake CUPS objects replacing the ``cups`` and ``cups_notify`` bindings
of the ``pibooth.printer`` module.
"""

# States defined at: https://www.rfc-editor.org/rfc/rfc8011#section-5.4.11
PRINTER_STATE_IDLE = 3
PRINTER_STATE_PROCESSING = 4
PRINTER_STATE_STOPPED = 5


class CupsConnectionMock:

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

    CUPS_EVT_JOB_COMPLETED = 'job-completed'
    CUPS_EVT_JOB_CREATED = 'job-created'
    CUPS_EVT_JOB_STOPPED = 'job-stopped'
    CUPS_EVT_PRINTER_STATE_CHANGED = 'printer-state-changed'
    CUPS_EVT_PRINTER_STOPPED = 'printer-stopped'


class CupsModuleMock:

    def __init__(self, conn):
        self._conn = conn

    def Connection(self):
        return self._conn


class CupsUnreachableModuleMock:

    def Connection(self):
        raise RuntimeError("failed to connect to server")


class CupsNotificationMock:

    def __init__(self, title="Job completed"):
        self.title = title
