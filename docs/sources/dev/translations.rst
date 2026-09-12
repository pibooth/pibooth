Adding a translation
--------------------

All texts displayed by the interface live in ``pibooth/language.py``, in the
``DEFAULT`` dictionary keyed by two-letter language code. There is no ``gettext``
and no ``.po`` file.

Keys
^^^^

Every language section must define all of them. A missing key falls back to
English at runtime and logs a warning.

================== =========================================================
Key                Where it is displayed
================== =========================================================
``intro``          ``wait`` screen, main call to action
``intro_print``    ``wait`` screen, when the previous picture can be printed
``choose``         ``choose`` screen title
``1``              captures number choice — mind the singular and plural
``2``              idem
``3``              idem
``4``              idem
``chosen``         ``chosen`` screen, confirmation
``smile``          displayed during ``preview`` and ``capture``
``processing``     ``processing`` screen
``print``          ``print`` screen question
``print_forget``   displayed when the user declines the print
``finished``       ``finish`` screen
``oops``           ``failsafe`` screen
================== =========================================================

Adding a language
^^^^^^^^^^^^^^^^^

1. Insert a new section in ``DEFAULT``, **in alphabetical order** of the
   two-letter code users will put in ``[GENERAL][language]``.
2. Copy the ``en`` block and translate every value, leaving the keys untouched.
3. Keep the ``\n`` line breaks. They are manual line wrapping for narrow areas
   of the screen, especially ``intro_print`` and ``print_forget``. Staying close
   to the number of lines and the line length used by the other languages avoids
   text overflowing its area.
4. Add the language to the ``Natural Language ::`` classifiers in ``setup.py``
   and to the feature list in ``README.rst``.

Nothing else has to be registered: ``get_supported_languages()`` and the
settings menu pick the new section up automatically.

Things to know
^^^^^^^^^^^^^^

* Values are plain Python strings, so mind the quoting — an apostrophe forces
  double quotes, as in ``"C'est parti !"``.
* The file is UTF-8, so accented and non-latin characters are fine **provided
  the font can render them**. The default fonts, ``Amatic-Bold`` and
  ``AmaticSC-Regular``, have a limited coverage: a language using Cyrillic,
  Greek or CJK characters also requires the user to set ``[WINDOW][font]``.
* Users can override any text in ``~/.config/pibooth/translations.cfg``, edited
  with ``pibooth --translate``. Adding a key or a language is not destructive
  for existing installations: the defaults are merged into the user file.

Checking
^^^^^^^^

All sections should define exactly the same keys::

    python - <<'EOF'
    from pibooth.language import DEFAULT
    reference = set(DEFAULT['en'])
    for code, texts in DEFAULT.items():
        missing, extra = reference - set(texts), set(texts) - reference
        if missing or extra:
            print(code, 'missing:', missing, 'extra:', extra)
    EOF

Then regenerate the translations file to see what users will get, without
touching your own configuration::

    pibooth --reset /tmp/piboothcfg
    cat /tmp/piboothcfg/translations.cfg
