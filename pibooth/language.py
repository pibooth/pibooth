# -*- coding: utf-8 -*-

"""Pibooth language handling.
"""

import io
import os
import os.path as osp
from pibooth.utils import LOGGER, open_text_editor

try:
    from configparser import ConfigParser
except ImportError:
    # Python 2.x fallback
    from ConfigParser import ConfigParser

PARSER = ConfigParser()

CURRENT = 'en'  # Dynamically set at startup

DEFAULT = {
    'en': {
        'intro': "Take a photo",
        'intro_print': "Or you can\nstill print\nthis photo",
        'choose': "Choose your layout",
        '1': "1 photo",
        '2': "2 photos",
        '3': "3 photos",
        '4': "4 photos",
        'chosen': "Let's go!",
        'smile': "Smile !",
        'processing': "Processing...",
        'print': "Print the photo?",
        'finished': "Thanks",
        'oops': "Oops something went wrong",
    },
    'es': {
        'intro': "Sacate Una Foto",
        'intro_print': "O Puedes\nTodavia Imprimir\nEsta Foto",
        'choose': "Elige el tipo de foto",
        '1': "1 Foto",
        '2': "2 Fotos",
        '3': "3 Fotos",
        '4': "4 Fotos",
        'chosen': "Adelante!!",
        'smile': "Sonríe!!",
        'processing': "Procesando...",
        'print': "Imprimir esta foto?",
        'finished': "Gracias",
        'oops': "Maldición! Algo salió mal",
    },
    'fr': {
        'intro': "Faire une photo",
        'intro_print': "Ou sinon\ntu peux toujours\nimprimer\ncette photo",
        'choose': "Choisis ton format",
        '1': "1 photo",
        '2': "2 photos",
        '3': "3 photos",
        '4': "4 photos",
        'chosen': "C'est parti !",
        'smile': "Souriez !",
        'processing': "Préparation du montage",
        'print': "Imprimer la photo ?",
        'finished': "Merci",
        'oops': "Oups quelque chose s'est mal passé",
    },
    'de': {
        'intro': "Foto aufnehmen",
        'intro_print': "Sie können dieses\nfoto immer noch\nausdrucken",
        'choose': "Wähle dein Layout",
        '1': "1 foto",
        '2': "2 fotos",
        '3': "3 fotos",
        '4': "4 fotos",
        'chosen': "Los gehts!",
        'smile': "Bitte lächeln !",
        'processing': "Bearbeitung...",
        'print': "Foto drucken?",
        'finished': "Danke",
        'oops': "Ups Irgendwas lief schief",
    },
    'nl': {
        'intro': "Neem een foto",
        'intro_print': "Of je kan\nnog altijd \ndeze foto printen",
        'choose': "Kies een ontwerp",
        '1': "1 foto",
        '2': "2 foto’s",
        '3': "3 foto’s",
        '4': "4 foto’s",
        'chosen': "We gaan ervoor!",
        'smile': "Lachen !",
        'processing': "Verwerken...",
        'print': "Print de foto?",
        'finished': "Bedankt",
        'oops': "Oeps er ging iets mis",
    }
}


def init(filename, clear=False):
    """Initialize the translation system.

    :param filename: path to the translations file
    :type filename: str
    :param clear: restore default translations
    :type clear: bool
    """
    PARSER.filename = osp.abspath(osp.expanduser(filename))

    if not osp.isfile(PARSER.filename) or clear:
        LOGGER.info("Generate the translation file in '%s'", PARSER.filename)
        dirname = osp.dirname(PARSER.filename)
        if not osp.isdir(dirname):
            os.makedirs(dirname)

        with io.open(PARSER.filename, 'w', encoding="utf-8") as fp:
            for section, options in DEFAULT.items():
                fp.write("[{}]\n".format(section))
                for name, value in options.items():
                    value = value.splitlines()
                    fp.write("{} = {}\n".format(name, value[0]))
                    if len(value) > 1:
                        for part in value[1:]:
                            fp.write("    {}\n".format(part))
                fp.write("\n\n")

    PARSER.read(PARSER.filename, encoding='utf-8')


def edit():
    """Open a text editor to edit the translations.
    """
    if not getattr(PARSER, 'filename', None):
        raise EnvironmentError("Translation system is not initialized")

    open_text_editor(PARSER.filename)


def get_supported_languages():
    """Return the list of supported language.
    """
    if getattr(PARSER, 'filename', None):
        return [lang for lang in PARSER.sections()]
    return list(DEFAULT.keys())


def get_translated_text(key):
    """Return the text corresponding to the key in the language defined in the config.

    :param key: key in the translation file
    :type key: str
    """
    if not getattr(PARSER, 'filename', None):
        raise EnvironmentError("Translation system is not initialized")

    if PARSER.has_section(CURRENT) and PARSER.has_option(CURRENT, key):
        return PARSER.get(CURRENT, key).strip('"')
    elif PARSER.has_option('en', key):
        LOGGER.warning("Unsupported language '%s', fallback to English", CURRENT)
        return PARSER.get('en', key).strip('"')

    LOGGER.debug("No translation defined for '%s/%s' key", CURRENT, key)
    return None
