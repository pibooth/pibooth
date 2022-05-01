# -*- coding: utf-8 -*-

"""A photo booth application in pure Python for the Raspberry Pi."""

__version__ = "2.0.5"

try:

    import pluggy

    # Marker to be imported and used in plugins (and for own implementations)
    hookimpl = pluggy.HookimplMarker('pibooth')

except ImportError:
    pass  # When running the setup.py, pluggy is not yet installed
