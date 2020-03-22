# -*- coding: utf-8 -*-

"""A photo booth application in pure Python for the Raspberry Pi."""

__version__ = "1.2.0"

import pluggy

# Marker to be imported and used in plugins (and for own implementations)
hookimpl = pluggy.HookimplMarker('pibooth')
