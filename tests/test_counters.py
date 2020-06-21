# -*- coding: utf-8 -*-

import pytest


def test_iter(counters):
    for name in counters:
        assert name


def test_getitem(counters):
    assert counters['nbr_printed'] == 0


def test_names(counters):
    assert len(counters.names()) == 1
    assert 'nbr_printed' in counters.names()


def test_set(counters):
    assert counters.nbr_printed == 0
    counters.nbr_printed += 2
    assert counters.nbr_printed == 2


def test_reset(counters):
    counters.nbr_printed = 5
    assert counters.nbr_printed == 5
    counters.reset()
    assert counters.nbr_printed == 0


def test_invalid_counter(counters):
    with pytest.raises(AttributeError):
        counters.invalid


def test_save(counters):
    counters.nbr_printed = 5
    counters.data['nbr_printed'] = 0
    assert counters.nbr_printed == 0
    counters.load()
    assert counters.nbr_printed == 5
    counters.reset()
    counters.load()
    assert counters.nbr_printed == 0
