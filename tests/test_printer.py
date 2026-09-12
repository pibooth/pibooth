# -*- coding: utf-8 -*-

import pytest
import pygame
import printer_drivers
from pibooth import printer as printer_module
from pibooth.counters import Counters
from pibooth.printer import Printer, PRINTER_TASKS_UPDATED


def test_installed(printer):
    assert printer.is_installed()
    assert printer.is_ready()
    assert printer.name == 'fake-printer'


def test_not_installed(monkeypatch):
    monkeypatch.setattr(printer_module, 'cups', None)
    printer = Printer()
    assert not printer.is_installed()
    assert not printer.is_ready()
    assert printer.get_all_tasks() == {}
    with pytest.raises(EnvironmentError):
        printer.print_file(__file__)
    printer.quit()


def test_cups_server_unreachable(monkeypatch):
    monkeypatch.setattr(printer_module, 'cups', printer_drivers.CupsUnreachableModuleMock())
    monkeypatch.setattr(printer_module, 'Subscriber', printer_drivers.CupsSubscriberMock, raising=False)
    printer = Printer()
    assert printer._conn is None
    assert printer._notifier is None
    assert printer.name is None
    assert not printer.is_installed()
    assert not printer.is_ready()
    assert printer.get_all_tasks() == {}
    with pytest.raises(EnvironmentError):
        printer.print_file(__file__)
    with pytest.raises(EnvironmentError):
        printer.cancel_all_tasks()
    printer.quit()


def test_no_printer_in_cups(cups_conn):
    cups_conn.printers.clear()
    cups_conn.default = None
    printer = Printer()
    assert not printer.is_installed()
    assert not printer.is_ready()


def test_unknown_printer_name(cups_conn):
    assert not Printer('other-printer').is_installed()
    assert Printer('fake-printer').is_installed()


def test_take_first_printer(cups_conn):
    cups_conn.default = None
    assert Printer().name == 'fake-printer'


def test_max_pages(cups_conn, tmpdir):
    counters = Counters(str(tmpdir.join('counters.json')), printed=1)
    printer = Printer(max_pages=2, counters=counters)
    assert printer.is_ready()
    counters.printed = 2
    assert not printer.is_ready()


def test_print_file(printer, cups_conn, fond_path):
    printer.print_file(fond_path)
    assert cups_conn.printed_files == [('fake-printer', fond_path, {})]
    assert printer._notifier.is_subscribed(printer._on_event)
    assert len(printer.get_all_tasks()) == 1
    printer.cancel_all_tasks()
    assert printer.get_all_tasks() == {}
    printer.quit()
    assert not printer._notifier.is_subscribed(printer._on_event)


def test_print_file_copies(printer, cups_conn, fond_path):
    printer.print_file(fond_path, copies=2)
    assert len(cups_conn.printed_files) == 1
    assert cups_conn.printed_files[0][0] == 'fake-printer'
    assert cups_conn.printed_files[0][1] != fond_path  # A temporary composed page is printed


def test_print_missing_file(printer, tmpdir):
    with pytest.raises(IOError):
        printer.print_file(str(tmpdir.join('missing.jpg')))


def test_printer_options(cups_conn, fond_path):
    printer = Printer(options={'media': 'A4'})
    printer.print_file(fond_path)
    assert cups_conn.printed_files[-1][2] == {'media': 'A4'}
    assert Printer(options='invalid').options == {}


def test_notification_event(printer):
    pygame.display.init()  # Do not call set_mode(): the display is shared with test_window.py
    pygame.event.clear()
    printer._on_event(printer_drivers.CupsNotificationMock("Job completed"))
    events = [evt for evt in pygame.event.get() if evt.type == PRINTER_TASKS_UPDATED]
    assert len(events) == 1
    assert events[0].evt.title == "Job completed"


def test_notification_error_is_logged(printer, monkeypatch, caplog):
    def raise_error(*args, **kwargs):
        raise RuntimeError("video system not initialized")
    monkeypatch.setattr(pygame.event, 'post', raise_error)
    printer._on_event(printer_drivers.CupsNotificationMock())
    assert "Error while handling printer event" in caplog.text
