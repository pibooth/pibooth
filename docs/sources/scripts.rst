.. _scripts:

Tools and scripts
-----------------

List available fonts
^^^^^^^^^^^^^^^^^^^^

The available fonts can be listed using the following the command:

.. code-block:: bash

    pibooth-fonts

*Output example*::

    [ INFO    ] pibooth           : Listing all fonts available...
    acaslonprobold            gurmukhi                    prestigeelitestdbd
    acaslonprobolditalic      gurmukhimn                  ptmono
    acaslonproitalic          gurmukhisangammn            ptsans
    acaslonproregular         hellohoney                  ptserif
    acaslonprosemibold        helvetica                   ptserifcaption
    ...

Regenerate pictures
^^^^^^^^^^^^^^^^^^^

To regenerate the final pictures afterwards, from the originals captures present in the
``raw`` folder, use the command:

.. code-block:: bash

    pibooth-regen

It permits to adjust the configuration to enhance the previous pictures with better
parameters (title, more effects, etc...)

Manage counters
^^^^^^^^^^^^^^^

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

The output can be formated in **json** using the ``--json`` option:

.. code-block:: bash

    pibooth-count --json

*Output example*::

    {"taken": 126, "printed": 17, "forgotten": 2, "remaining_duplicates": 3}

The counters can be updated/rest using the ``--update`` option:

.. code-block:: bash

    pibooth-count --update

Errors diagnosis
^^^^^^^^^^^^^^^^

Use the following command to generate a debug report on your Raspberry-Pi, then
paste it in a GitHb issue to gives details about your ``pibooth`` environment:

.. code-block:: bash

    pibooth-diag
