# -*- coding: utf-8 -*-

import pytest
from pibooth import language


def test_supported_language(init_lang):
    assert 'en' in language.get_supported_languages()
    assert 'fr' in language.get_supported_languages()


def test_current(init_lang):
    with pytest.raises(AssertionError):
        language.set_current('be')
    language.set_current('fr')


def test_translate(init_lang):
    language.set_current('en')
    assert language.get_translated_text('finished') == "Thanks"
    language.set_current('fr')
    assert language.get_translated_text('finished') == "Merci"
