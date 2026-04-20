# -*- coding: utf-8 -*-

import json
import os
import pickle
import pytest
from pibooth.counters import Counters


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


def test_json_format(counters):
    """Verify counters are saved in JSON format."""
    counters.nbr_printed = 3
    assert counters.filename.endswith('.json')
    with open(counters.filename, 'r') as fp:
        data = json.load(fp)
    assert data['nbr_printed'] == 3


def test_migrate_pickle(tmpdir):
    """Verify legacy pickle files are migrated to JSON."""
    pickle_file = str(tmpdir.join('counters.pickle'))
    json_file = str(tmpdir.join('counters.json'))

    # Create a legacy pickle file
    with open(pickle_file, 'wb') as fp:
        pickle.dump({'nbr_printed': 42}, fp)

    # Load from pickle path — should migrate to JSON
    c = Counters(pickle_file, nbr_printed=0)
    assert c.nbr_printed == 42
    assert c.filename == json_file
    assert os.path.isfile(json_file)


def test_atomic_save(counters):
    """Verify no .tmp file is left after save."""
    counters.nbr_printed = 7
    assert not os.path.isfile(counters.filename + '.tmp')
