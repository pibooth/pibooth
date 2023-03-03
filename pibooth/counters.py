# -*- coding: utf-8 -*-

import pickle
import os.path as osp


class Counters(object):

    def __init__(self, filename='', **kwargs):
        self.data = kwargs.copy()
        self.default = kwargs
        self.filename = osp.abspath(osp.expanduser(filename))
        if osp.isfile(self.filename):
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

    def load(self):
        """Load the saved counters.
        """
        with open(self.filename, 'rb') as fp:
            self.data.update(pickle.load(fp))

    def reset(self):
        """Reset all counters.
        """
        self.data = self.default.copy()
        self.save()

    def save(self):
        """Save the current counters in a file.
        """
        with open(self.filename, 'wb') as fp:
            pickle.dump(self.data, fp, pickle.HIGHEST_PROTOCOL)
