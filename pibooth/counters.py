# -*- coding: utf-8 -*-

import os
import os.path as osp
import json
import pickle
from pibooth.utils import LOGGER


class Counters(object):

    """Persistent counters stored in a JSON file. A ``.pickle`` file written
    by a previous version of pibooth, next to the JSON one, is migrated on
    first load.
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
        return ", ".join("{}:{}".format(key, value) for key, value in self.data.items())

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
            raise AttributeError("No counter with name '{}'".format(name))
        return self.data[name]

    def __setattr__(self, name, value):
        """Called each time an attribute is set.
        """
        if name != 'data' and name in self.data:
            self.data[name] = value
            self.save()
        else:
            super(Counters, self).__setattr__(name, value)

    def names(self):
        """Return the list of counters.
        """
        return [key for key in self.data]

    def _migrate_pickle(self):
        """Load the counters from the legacy pickle file and save them in
        the JSON one.
        """
        try:
            with open(self.legacy_filename, 'rb') as fp:
                data = pickle.load(fp)
            if not isinstance(data, dict):
                raise ValueError("expected a dict, got {}".format(type(data).__name__))
            self.data.update(data)
            LOGGER.info("Counters migrated from '%s' to '%s'", self.legacy_filename, self.filename)
        except Exception as ex:
            LOGGER.warning("Can not migrate counters from '%s' (%s), resetting counters",
                           self.legacy_filename, ex)
            self.data = self.default.copy()
        self.save()

    def load(self):
        """Load the saved counters.
        """
        if osp.isfile(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as fp:
                    data = json.load(fp)
                if not isinstance(data, dict):
                    raise ValueError("expected a dict, got {}".format(type(data).__name__))
                self.data.update(data)
            except (OSError, ValueError) as ex:
                LOGGER.warning("File '%s' corrupted (%s), resetting counters", self.filename, ex)
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
        """Save the current counters in the JSON file (atomic write).
        """
        tmp_filename = self.filename + '.tmp'
        try:
            with open(tmp_filename, 'w', encoding='utf-8') as fp:
                json.dump(self.data, fp, indent=2)
            os.replace(tmp_filename, self.filename)
        except OSError as ex:
            LOGGER.error("Failed to save counters in '%s': %s", self.filename, ex)
            if osp.isfile(tmp_filename):
                os.remove(tmp_filename)
