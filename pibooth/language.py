# -*- coding: utf-8 -*-

"""Pibooth language handling.
"""

import io
import os
import os.path as osp
from configparser import ConfigParser
from pibooth.utils import LOGGER, open_text_editor


PARSER = ConfigParser()

CURRENT = 'en'  # Dynamically set at startup

DEFAULT = {
    'de': {
        'intro': "Foto aufnehmen",
        'intro_print': "Du kannst dieses\nFoto immer noch\nausdrucken",
        'choose': "Wähle Dein Layout",
        '1': "1 Foto",
        '2': "2 Fotos",
        '3': "3 Fotos",
        '4': "4 Fotos",
        'chosen': "Los geht's!",
        'smile': "Bitte lächeln!",
        'processing': "Bearbeitung...",
        'print': "Foto drucken?",
        'print_forget': "Dieses Foto\nbitte löschen",
        'finished': "Danke",
        'oops': "Ups! Etwas ist schiefgelaufen",
    },
    'dk': {
        'intro': "Tag et foto",
        'intro_print': 'Eller du kan\nstadig udskrive\ndette foto',
        'choose': "Vælg dit layout",
        '1': "1 Foto",
        '2': "2 Fotos",
        '3': "3 Fotos",
        '4': "4 Fotos",
        'chosen': "Gør dig klar!",
        'smile': "Smil !",
        'processing': "Fremkalder Foto...",
        'print': "Print foto?",
        'print_forget': "Venligst\nglem dette\nfoto",
        'finished': "Tak",
        'oops': "Ups! Noget gik galt",
    },
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
        'print_forget': "Please\nforget this\nphoto",
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
        'print': "¿Imprimir esta foto?",
        'print_forget': "Por favor\nolvida\nesta foto",
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
        'print_forget': "Oublie\ncette photo\ns'il te plait",
        'finished': "Merci",
        'oops': "Oups quelque chose s'est mal passé",
    },
    'hu': {
        'intro': "Akarsz egy képet",
        'intro_print': 'Vagy\nkinyomtathatja\nezt a fényképet',
        'choose': "Kérlek válassz",
        '1': "1 kép",
        '2': "2 kép",
        '3': "3 kép",
        '4': "4 kép",
        'chosen': "Készülj!",
        'smile': "Csiizzz!",
        'processing': "Feldolgozás...",
        'print': "Nyomtatod a képet?",
        'print_forget': "Kérjük,\nfelejtsd el ezt\na képet",
        'finished': "Köszi",
        'oops': "Sajnos valami hiba történt",
    },
    'it': {
        'intro': "Scatta una foto", 
        'intro_print': 'Oppure puoi\nstampare\nquesta foto',
        'choose': "Scegli il formato",
        '1': "1 foto",
        '2': "2 foto",
        '3': "3 foto",
        '4': "4 foto",
        'chosen': "Andiamo!",
        'smile': "Sorridi!",
        'processing': "Elaborazione...",
        'print': "Stampo la foto?",
        'print_forget': "Per favore\nignora questa\nfoto",
        'finished': "Grazie",
        'oops': "Oops qualcosa è andato storto",
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
        'smile': "Lachen!",
        'processing': "Verwerken...",
        'print': "Print de foto?",
        'print_forget': "Vergeet\ndeze foto\nalstublieft",
        'finished': "Bedankt",
        'oops': "Oeps er ging iets mis",
    },
    'no': {
        'intro': "Ta et bilde",
        'intro_print': 'Eller du kan\nfremdeles printe\ndette bildet',
        'choose': "Velg ditt utseende",
        '1': "1 bilde",
        '2': "2 bilder",
        '3': "3 bilder",
        '4': "4 bilder",
        'chosen': "Start!",
        'smile': "Smil !",
        'processing': "Behandler...",
        'print': "Printe bildet?",
        'print_forget': "Glem\ndette\nbildet",
        'finished': "Takk",
        'oops': "Ops, noe gikk galt",
    },
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

    # Update the current file with missing language(s) and key(s)
    changed = False
    for section, options in DEFAULT.items():
        if not PARSER.has_section(section):
            changed = True
            LOGGER.debug("Add [%s] to available language list", section)
            PARSER.add_section(section)

        for option, value in options.items():
            if not PARSER.has_option(section, option):
                changed = True
                LOGGER.debug("Add [%s][%s] to available translations", section, option)
                PARSER.set(section, option, value)

    if changed:
        with io.open(PARSER.filename, 'w', encoding="utf-8") as fp:
            PARSER.write(fp)


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
        return list(sorted(lang for lang in PARSER.sections()))
    return list(sorted(DEFAULT.keys()))


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
