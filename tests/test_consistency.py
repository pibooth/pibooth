# -*- coding: utf-8 -*-

"""Checks of the files maintained by hand next to the code."""

import os
import re
import sys
import difflib
import subprocess
import os.path as osp
from pibooth.language import DEFAULT

ROOT = osp.dirname(osp.dirname(osp.abspath(__file__)))


def test_translations_define_the_same_keys():
    reference = set(DEFAULT['en'])
    for code, texts in DEFAULT.items():
        assert set(texts) == reference, "language '{}'".format(code)


def test_languages_have_a_classifier():
    with open(osp.join(ROOT, 'setup.py'), encoding='utf-8') as fp:
        classifiers = re.findall(r"'Natural Language :: ", fp.read())
    assert len(classifiers) == len(DEFAULT)


def test_documented_default_config_is_up_to_date(tmpdir):
    env = dict(os.environ, SDL_VIDEODRIVER='dummy')
    subprocess.run([sys.executable, '-m', 'pibooth', '--reset', str(tmpdir)], check=True, env=env)
    with open(str(tmpdir.join('pibooth.cfg')), encoding='utf-8') as fp:
        generated = fp.read().rstrip('\n').splitlines()
    with open(osp.join(ROOT, 'docs', 'sources', 'config', 'default.cfg'), encoding='utf-8') as fp:
        documented = fp.read().rstrip('\n').splitlines()
    diff = list(difflib.unified_diff(documented, generated, 'docs/sources/config/default.cfg', 'pibooth --reset', lineterm=''))
    assert not diff, "\n".join(diff)
