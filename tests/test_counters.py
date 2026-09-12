# -*- coding: utf-8 -*-

import os
import json
import pickle
import os.path as osp
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
    counters.nbr_printed = 3
    assert counters.filename.endswith('.json')
    with open(counters.filename, 'r', encoding='utf-8') as fp:
        assert json.load(fp) == {'nbr_printed': 3}


def test_no_temporary_file_left(counters):
    counters.nbr_printed = 3
    assert not osp.exists(counters.filename + '.tmp')
    assert os.listdir(osp.dirname(counters.filename)) == [osp.basename(counters.filename)]


def test_migrate_from_pickle(tmpdir):
    legacy = str(tmpdir.join('counters.pickle'))
    with open(legacy, 'wb') as fp:
        pickle.dump({'taken': 42, 'printed': 7}, fp, pickle.HIGHEST_PROTOCOL)

    counters = Counters(str(tmpdir.join('counters.json')), taken=0, printed=0, forgotten=0)
    assert counters.taken == 42
    assert counters.printed == 7
    assert counters.forgotten == 0
    assert osp.isfile(counters.filename)
    with open(counters.filename, 'r', encoding='utf-8') as fp:
        assert json.load(fp) == {'taken': 42, 'printed': 7, 'forgotten': 0}

    # The JSON file is now the reference, the pickle one is no more read
    with open(legacy, 'wb') as fp:
        pickle.dump({'taken': 1000}, fp, pickle.HIGHEST_PROTOCOL)
    counters = Counters(str(tmpdir.join('counters.json')), taken=0, printed=0, forgotten=0)
    assert counters.taken == 42


def test_pickle_filename_is_converted_to_json(tmpdir):
    with open(str(tmpdir.join('counters.pickle')), 'wb') as fp:
        pickle.dump({'taken': 5}, fp, pickle.HIGHEST_PROTOCOL)
    counters = Counters(str(tmpdir.join('counters.pickle')), taken=0)
    assert counters.filename == str(tmpdir.join('counters.json'))
    assert counters.taken == 5


def test_corrupted_pickle(tmpdir):
    with open(str(tmpdir.join('counters.pickle')), 'wb') as fp:
        fp.write(b'\x80\x05 garbage')
    counters = Counters(str(tmpdir.join('counters.json')), taken=0)
    assert counters.taken == 0
    with open(counters.filename, 'r', encoding='utf-8') as fp:
        assert json.load(fp) == {'taken': 0}


@pytest.mark.parametrize('content', ['{"taken": 3', '', '[1, 2]', '"taken"'])
def test_corrupted_json(tmpdir, content):
    filename = str(tmpdir.join('counters.json'))
    with open(filename, 'w', encoding='utf-8') as fp:
        fp.write(content)
    counters = Counters(filename, taken=0, printed=0)
    assert counters.taken == 0
    assert counters.printed == 0
    with open(filename, 'r', encoding='utf-8') as fp:
        assert json.load(fp) == {'taken': 0, 'printed': 0}
    assert not osp.exists(filename + '.tmp')
