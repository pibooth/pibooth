# -*- coding: utf-8 -*-

import json
import os
import os.path as osp
import pickle
from pibooth.utils import LOGGER


class Counters:

    def __init__(self, filename='', **kwargs):
        self.data = kwargs.copy()
        self.default = kwargs
        self.filename = osp.abspath(osp.expanduser(filename))
        # Check both pickle and json files for backward compatibility
        json_file = self.filename.replace('.pickle', '.json')
        if osp.isfile(json_file) or osp.isfile(self.filename):
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
            with open(self.filename, 'rb') as fp:
                self.data.update(pickle.load(fp))
            LOGGER.info("Migrated counters from pickle to JSON format")
            self.save()
        except (pickle.UnpicklingError, EOFError, Exception) as ex:
            LOGGER.warning("Could not migrate pickle counters: %s", ex)

    def load(self):
        """Load the saved counters.
        """
        json_file = self.filename.replace('.pickle', '.json')

        if osp.isfile(json_file):
            self.filename = json_file
            try:
                with open(self.filename, 'r') as fp:
                    self.data.update(json.load(fp))
                return
            except (json.JSONDecodeError, ValueError):
                LOGGER.warning("File '%s' corrupted, resetting counters", self.filename)
                self.data = self.default.copy()
                self.save()
                return

        # Legacy pickle file: migrate to JSON
        if osp.isfile(self.filename) and self.filename.endswith('.pickle'):
            self._migrate_pickle()
            self.filename = json_file
            self.save()
            return

    def reset(self):
        """Reset all counters.
        """
        self.data = self.default.copy()
        self.save()

    def save(self):
        """Save the current counters in a JSON file (atomic write).
        """
        if self.filename.endswith('.pickle'):
            self.filename = self.filename.replace('.pickle', '.json')

        tmp_file = self.filename + '.tmp'
        try:
            with open(tmp_file, 'w') as fp:
                json.dump(self.data, fp, indent=2)
            os.replace(tmp_file, self.filename)
        except OSError as ex:
            LOGGER.error("Failed to save counters: %s", ex)
            if osp.isfile(tmp_file):
                os.remove(tmp_file)
