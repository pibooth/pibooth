# -*- coding: utf-8 -*-

import pytest
from pibooth import printer as printer_module
from pibooth.counters import Counters
from pibooth.printer import Printer, PRINTER_STATE_IDLE, PRINTER_STATE_PROCESSING, PRINTER_STATE_STOPPED


def test_installed(printer):
    assert printer.is_installed()
    assert printer.name == 'fake-printer'


def test_ready(printer):
    assert printer.is_ready()
    assert printer.state == PRINTER_STATE_IDLE


def test_not_installed(monkeypatch):
    monkeypatch.setattr(printer_module, 'cups', None)
    printer = Printer()
    assert not printer.is_installed()
    assert not printer.is_ready()
    assert printer.get_all_tasks() == {}
    with pytest.raises(EnvironmentError):
        printer.print_file(__file__)


def test_no_printer_in_cups(cups_conn):
    cups_conn.printers.clear()
    cups_conn.default = None
    printer = Printer()
    assert not printer.is_installed()
    assert not printer.is_ready()


def test_unknown_printer_name(cups_conn):
    printer = Printer('other-printer')
    assert not printer.is_installed()
    assert Printer('fake-printer').is_installed()


def test_take_first_printer(cups_conn):
    cups_conn.default = None
    assert Printer().name == 'fake-printer'


def test_connection_failure(monkeypatch):
    class FailingCupsMock:

        def Connection(self):
            raise IOError("CUPS server not running")

    monkeypatch.setattr(printer_module, 'cups', FailingCupsMock())
    printer = Printer()
    assert printer.name is None
    assert not printer.is_installed()


def test_ipp_state_processing(printer, cups_conn):
    cups_conn.printers['fake-printer']['printer-state'] = PRINTER_STATE_PROCESSING
    assert printer.is_ready()
    assert printer.state == PRINTER_STATE_PROCESSING


def test_ipp_state_stopped(printer, cups_conn):
    cups_conn.printers['fake-printer']['printer-state'] = PRINTER_STATE_STOPPED
    cups_conn.printers['fake-printer']['printer-state-reasons'] = ['media-empty-error']
    assert not printer.is_ready()
    assert printer.state == PRINTER_STATE_STOPPED


def test_reenable_paused_printer(printer, cups_conn):
    cups_conn.printers['fake-printer']['printer-state'] = PRINTER_STATE_STOPPED
    cups_conn.printers['fake-printer']['printer-state-reasons'] = ['paused']
    # First call re-enables the printer but reports it as not ready
    assert not printer.is_ready()
    assert cups_conn.printers['fake-printer']['printer-state'] == PRINTER_STATE_IDLE
    assert printer.is_ready()
    assert printer.state == PRINTER_STATE_IDLE


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


def test_print_missing_file(printer, tmpdir):
    with pytest.raises(IOError):
        printer.print_file(str(tmpdir.join('missing.jpg')))


def test_printer_options(cups_conn, fond_path):
    printer = Printer(options={'media': 'A4'})
    printer.print_file(fond_path)
    assert cups_conn.printed_files[-1][2] == {'media': 'A4'}
    assert Printer(options='invalid').options == {}
