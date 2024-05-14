.. _scripts:

List available fonts
--------------------

The available fonts can be listed using the following the command:

.. code-block:: bash

    pibooth-fonts

*Output example*::

    INFO:pibooth:Listing all fonts available...
    acaslonprobold            gurmukhi                    prestigeelitestdbd
    acaslonprobolditalic      gurmukhimn                  ptmono
    acaslonproitalic          gurmukhisangammn            ptsans
    acaslonproregular         hellohoney                  ptserif
    acaslonprosemibold        helvetica                   ptserifcaption
    ...

Regenerate pictures
-------------------

To regenerate the final pictures afterwards, from the originals captures present in the
``raw`` folder, use the command:

.. code-block:: bash

    pibooth-regen

It permits to adjust the configuration to enhance the previous pictures with better
parameters (title, more effects, etc...)

Like with the ``pibooth`` application a configuration directory can be chosen.

.. code-block:: bash

    pibooth-regen myconfig1/

Manage counters
---------------

Several counters are registered during ``pibooth`` usage to keep in track the
number of:

- **taken** pictures since last reset
- **printed** pictures since last reset
- **forgotten** pictures since last reset
- remaining duplicate for the currently displayed picture

Pictures counters can be displayed using the command:

.. code-block:: bash

    pibooth-count

*Output example*::

    Listing current counters:

     -> Taken.................... :  126
     -> Printed.................. :   17
     -> Forgotten................ :    2
     -> Remaining_duplicates..... :    3

The output can be formatted in **json** using the ``--json`` option:

.. code-block:: bash

    pibooth-count --json

*Output example*::

    {"taken": 126, "printed": 17, "forgotten": 2, "remaining_duplicates": 3}

The counters can be updated/rest using the ``--update`` option:

.. code-block:: bash

    pibooth-count --update

Errors diagnosis
----------------

Use the following command to generate a debug report on your Raspberry-Pi, then
paste it in a GitHb issue to gives details about your ``pibooth`` environment:

.. code-block:: bash

    pibooth-diag

List printer options
--------------------

Use the following command to list all options as defined in the
`PPD <https://www.cups.org/doc/spec-ppd.html>`_ file of the printer defined
in the configuration:

.. code-block:: bash

    pibooth-printcfg

*Output example*::

    INFO:pibooth:Connected to printer 'EPSON_XP_6100_Series'
    EPIJ_PSrc = 2
         Description: Page Setup
         Choices:     2 = Standard
                      3 = Borderless
                      25 = CD/DVD

    EPIJ_Size = 1
         Description: Paper Size
         Choices:     1 = A4
                      74 = 10 x 15 cm (4 x 6 in)
                      76 = 13 x 18 cm (5 x 7 in)
                      6 = A6
                      23 = A5
    ...

The current values can be formatted in **json** using the ``--json`` option, the
generated output can be pasted (after update of the wanted values) in the 
``[PRINTER][printer_options]`` option:

.. code-block:: bash

    pibooth-printcfg --json

*Output example*::

    {"EPIJ_PSrc": "2", "EPIJ_Size": "1", "EPIJ_FdSo": "11", "EPIJ_Medi": "0", "EPIJ_Ink_": "1",
    "EPIJ_DSPT": "0", "EPIJ_OpAv": "0", "EPIJProfileSpec": "0", "ColorModel": "RGB",
    "MediaType": "0", "Resolution": "360x360dpi", "PageSize": "A4", "PageRegion": "A4",
    "EPIJ_PGEx": "0", "EPIJ_BSSv": "0", "EPIJ_Silt": "0", "EPIJ_BkPr": "1", "EPIJ_AuCS": "1"}
