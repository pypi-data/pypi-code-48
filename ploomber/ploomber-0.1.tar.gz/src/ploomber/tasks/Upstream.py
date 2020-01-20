from copy import copy
import warnings
from collections import defaultdict, abc


class Upstream(abc.Mapping):
    """
    Mapping for representing upstream tasks, it's a collections.OrderedDict
    under the hood with an added .pop(key) method (like the one in a regular
    dictionary) and with a .first attribute, that returns the first value,
    useful when there is only one key-value pair.

    Used for task upstream dependencies, when employed as a context manager,
    it raises a warning if any of the elements was not used at least once,
    which means there are unused upstream dependencies
    """

    def __init__(self, data=None):
        self._dict = (data or {})
        self._init_counts()
        self._in_context = False

    # we cannot define this inside _init_counts or as a lambda, that does
    # not work with pickle
    def _zero():
        return 0

    def _init_counts(self):
        # lambdas do not work with pickle, must define a function
        self._counts = defaultdict(self._zero,
                                   {key: 0 for key in self._dict.keys()})

    @property
    def first(self):
        if not self._dict:
            raise KeyError('Cannot obtain first upstream task, the Task has '
                           'no upstream dependencies declared')

        first_key = next(iter(self._dict))
        return self._dict[first_key]

    def pop(self, key):
        return self._dict.pop(key)

    def to_dict(self):
        return copy(self._dict)

    def __getitem__(self, key):
        if self._in_context:
            self._counts[key] += 1

        try:
            return self._dict[key]
        except KeyError:
            raise KeyError('Cannot obtain upstream dependency named '
                           '{}, declared dependencies are: {}'
                           .format(key, self))

    def __setitem__(self, key, value):
        self._dict[key] = value

    def __iter__(self):
        for name in self._dict.keys():
            yield name

    def __len__(self):
        return len(self._dict)

    def __enter__(self):
        self._in_context = True
        self._init_counts()
        return self

    def __str__(self):
        return str(self._dict)

    def __repr__(self):
        return 'Upstream({})'.format(repr(self._dict))

    def __exit__(self, *exc):
        self._in_context = False
        unused = set([key for key, count in self._counts.items()
                      if count == 0])

        if unused:
            warnings.warn('The following parameters were not used {}'
                          .format(unused))
