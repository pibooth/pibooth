# -*- coding: utf-8 -*-

"""Pibooth language handling.
"""

from pibooth.config import PiConfigParser

LANGUAGES = {
    'fr': {
        'smile_message': "Souriez !",
        'intro': "Faire une photo",
        'intro_print': 'Ou sinon\ntu peux toujours\nimprimer\ncette photo',
        'oops': "Oops quelque chose s'est mal passé",
        'finished': "Merci",
        'choose': "Choisis ton format",
        'chosen': "C'est parti !",
        'processing': "Préparation du montage",
        'print': "Imprimer la photo ?"
    },
    'en': {
        'smile_message': "Smile !",
        'intro': "Take a photo",
        'intro_print': 'Or you can\nstill print\nthis photo',
        'oops': "Oops something went wrong",
        'finished': "Thanks",
        'choose': "Choose your layout",
        'chosen': "Let's go!",
        'processing': "Processing...",
        'print': "Print the photo?"
    },
    'de': {
        'smile_message': "Bitte lächeln !",
        'intro': "Foto aufnehmen",
        'intro_print': 'Sie können dieses\nfoto immer noch\nausdrucken',
        'oops': "Ups Irgendwas lief schief",
        'finished': "Danke",
        'choose': "Wähle dein Layout",
        'chosen': "Los gehts!",
        'processing': "Bearbeitung...",
        'print': "Foto drucken?"
    }
}

def get_translated_text(key):
    """Return the text corresponding to the key in the language defined in the config
    """
    try:
        return LANGUAGES[PiConfigParser.language].get(key)
    except KeyError:
        return LANGUAGES['en'].get(key)