# -*- coding: utf-8 -*-


def test_installed(printer):
    assert printer.is_installed()


def test_ready(printer):
    assert printer.is_ready()
