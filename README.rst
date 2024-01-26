|Pibooth|

|PythonVersions| |PypiPackage| |Downloads| |Tests| |Codecov|

The ``pibooth`` project provides a photobooth application *out-of-the-box* in pure Python
for Raspberry Pi. Have a look to the `wiki <https://github.com/pibooth/pibooth/wiki>`_
to discover some realizations from GitHub users, and don't hesitate to send us
photos of your version.

.. image:: https://raw.githubusercontent.com/pibooth/pibooth/master/docs/images/background_samples.png
   :align: center
   :alt: Settings

Features
--------

* Interface available in Danish, Dutch, English, French, German, Hungarian, Norwegian, Portuguese (Portugal and Brazil), Spanish and Swedish (customizable)
* Capture from 1 to 4 photos and concatenate them in a final picture
* Support all cameras compatible with gPhoto2, OpenCV and Raspberry Pi
* Support for hardware buttons and lamps on Raspberry Pi GPIO
* Fully driven from hardware buttons / keyboard / mouse / touchscreen
* Auto-start at the Raspberry Pi startup
* Animate captures from the last sequence during idle time
* Store final pictures and the individual captures
* Printing final pictures using CUPS server (printing queue indication)
* Custom texts can be added on the final picture (customizable fonts, colors, alignments)
* Custom background(s) and overlay(s) can be added on the final picture
* All settings available in a configuration file (most common options in a graphical interface)
* Highly customizable thanks to its plugin system, you can install
  `plugins developed by the community from PyPI  <https://pypi.org/search/?q=pibooth>`_
  or develop your own plugin.

Documentation
-------------

.. image:: https://raw.githubusercontent.com/pibooth/pibooth/master/docs/images/documentation.png
   :align: center
   :alt: Documentation
   :target: https://pibooth.readthedocs.io/en/stable
   :height: 200px

Plugins
-------

Here is a list of known plugins compatible with Pibooth

Pibooth organisation's plugin
=============================

- `pibooth-picture-template <https://github.com/pibooth/pibooth-picture-template>`_
- `pibooth-google-photo <https://github.com/pibooth/pibooth-google-photo>`_
- `pibooth-sound-effects <https://github.com/pibooth/pibooth-sound-effects>`_
- `pibooth_dropbox <https://github.com/pibooth/pibooth-dropbox>`_
- `pibooth-qrcode <https://github.com/pibooth/pibooth-qrcode>`_
- `pibooth-extra-lights <https://github.com/pibooth/pibooth-extra-lights>`_

Third-party plugins
===================

Third-party plugins can be found on GitHub or on `plugins on PyPI  <https://pypi.org/search/?q=pibooth>`_.
Here is a short list:

- `pibooth-lcd-display <https://pypi.org/project/pibooth-lcd-display>`_
- `pibooth-oled-display <https://pypi.org/project/pibooth-oled-display>`_
- `pibooth-neopixel_spi <https://github.com/peteoheat/pibooth-neopixel_spi>`_
- `pibooth-telegram-upload <https://pypi.org/project/pibooth-telegram-upload>`_
- `pibooth-s3-upload <https://pypi.org/project/pibooth-s3-upload>`_

Sponsors
--------

An enormous thanks to our sponsors:

- `@andhey <https://github.com/andhey>`_
- `@vo55 <https://github.com/vo55>`_
- `@laurammiller <https://github.com/laurammiller>`_
- `@neilrenfrey <https://github.com/neilrenfrey>`_
- `@agrovista <https://github.com/agrovista>`_ 
- `@mozdi <https://github.com/mozdi>`_
- `@MikkeBoomBoom <https://github.com/MikkeBoomBoom>`_
- `@fatgeek <https://github.com/fatgeek>`_

It means a lot to us!

.. |Pibooth| image:: https://raw.githubusercontent.com/pibooth/pibooth/master/docs/pibooth.png
   :align: middle

.. |PythonVersions| image:: https://img.shields.io/badge/python-3.6+-red.svg
   :target: https://www.python.org/downloads
   :alt: Python 3.6+

.. |PypiPackage| image:: https://badge.fury.io/py/pibooth.svg
   :target: https://pypi.org/project/pibooth
   :alt: PyPi package

.. |Downloads| image:: https://img.shields.io/pypi/dm/pibooth?color=purple
   :target: https://pypi.org/project/pibooth
   :alt: PyPi downloads

.. |Tests| image:: https://github.com/pibooth/pibooth/actions/workflows/tests.yml/badge.svg?branch=master
   :target: https://github.com/pibooth/pibooth/actions/workflows/tests.yml?query=branch%3Amaster
   :alt: Tests

.. |Codecov| image:: https://codecov.io/gh/pibooth/pibooth/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/pibooth/pibooth
    :alt: Codecov
