# -*- coding: utf-8 -*-

import json
import os
import os.path as osp
import pickle
from pibooth.utils import LOGGER


class Counters:

    """Persistent counters stored in a JSON file. A ``.pickle`` file written by
    a previous version, next to the JSON one, is migrated on first load.
    """

    def __init__(self, filename='', **kwargs):
        self.data = kwargs.copy()
        self.default = kwargs
        filename = osp.abspath(osp.expanduser(filename))
        if filename.endswith('.pickle'):
            filename = filename[:-len('.pickle')] + '.json'
        self.filename = filename
        self.legacy_filename = osp.splitext(filename)[0] + '.pickle'
        if osp.isfile(self.filename) or osp.isfile(self.legacy_filename):
            self.load()

    def __str__(self):
        return ", ".join(f"{key}:{value}" for key, value in self.data.items())

    def __iter__(self):
        """Iterate over counters names.
        """
        return iter(self.data)

    def __getitem__(self, name):
        """Get value from counter name.
        """
        return self.__getattr__(name)

    def __getattr__(self, name):
        """Called only when an attribute does not exist.
        """
        if name not in self.data:
            raise AttributeError(f"No counter with name '{name}'")
        return self.data[name]

    def __setattr__(self, name, value):
        """Called each time an attribute is set.
        """
        if name != 'data' and name in self.data:
            self.data[name] = value
            self.save()
        else:
            super().__setattr__(name, value)

    def names(self):
        """Return the list of counters.
        """
        return [key for key in self.data]

    def _migrate_pickle(self):
        """Migrate legacy pickle counters file to JSON format.
        """
        try:
            with open(self.legacy_filename, 'rb') as fp:
                self.data.update(pickle.load(fp))
            LOGGER.info("Migrated counters from '%s' to JSON format", self.legacy_filename)
        except Exception as ex:
            LOGGER.warning("Could not migrate pickle counters: %s", ex)
        self.save()

    def load(self):
        """Load the saved counters.
        """
        if osp.isfile(self.filename):
            try:
                with open(self.filename, 'r') as fp:
                    self.data.update(json.load(fp))
            except (json.JSONDecodeError, ValueError):
                LOGGER.warning("File '%s' corrupted, resetting counters", self.filename)
                self.data = self.default.copy()
                self.save()
        elif osp.isfile(self.legacy_filename):
            self._migrate_pickle()

    def reset(self):
        """Reset all counters.
        """
        self.data = self.default.copy()
        self.save()

    def save(self):
        """Save the current counters in a JSON file (atomic write).
        """
        tmp_file = self.filename + '.tmp'
        try:
            with open(tmp_file, 'w') as fp:
                json.dump(self.data, fp, indent=2)
            os.replace(tmp_file, self.filename)
        except OSError as ex:
            LOGGER.error("Failed to save counters: %s", ex)
            if osp.isfile(tmp_file):
                os.remove(tmp_file)
