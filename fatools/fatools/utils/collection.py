"""An general-purpose collection class.
"""

import collections
import operator

from fatools.utils.kernel import ensure_type


# TODO add tests
# TODO add docstring
class Collection(collections.Sequence):
    def __init__(self, items, sort_by=(), dtype=None, converter=None):
        self._dtype, self._converter = dtype, converter
        self._items = tuple(ensure_type(dtype, i, converter) for i in items)
        self.sort_keys = (sort_by,) if isinstance(sort_by, str) else sort_by
    sort_keys = property(lambda self: self._sort_keys)

    def __getitem__(self, item):
        return self._items[item]

    def __iter__(self):
        return iter(self._items)

    def __len__(self):
        return len(self._items)

    @sort_keys.setter
    def sort_keys(self, keys):
        assert isinstance(keys, (tuple, list)), 'invalid sort keys'
        self._sort_keys = tuple(keys)
        self.sort()

    def fetch_all(self, *items, **kwargs):
        getter = operator.attrgetter(*items)
        values = (getter(item) for item in self)
        if kwargs.get('uniq', False) is True:
            values = frozenset(values)
        if kwargs.get('exclude', ()):
            exclude = kwargs.get('exclude')
            if not isinstance(exclude, (tuple, list)):
                exclude = (exclude,)
            values = (val for val in values if val not in exclude)
        return tuple(values)

    def sort(self):
        self.sort_by(*self.sort_keys)

    def sort_by(self, *sort_keys):
        if not sort_keys:
            return
        self._items = sorted(self._items, key=operator.attrgetter(*sort_keys))


class MutableCollection(collections.MutableSequence, Collection):
    def __init__(self, *args, **kwargs):
        super(MutableCollection, self).__init__(*args, **kwargs)
        self._items = list(self._items)

    def __delitem__(self, i):
        self._items.__delitem__(i)

    def __setitem__(self, idx, item):
        self._items[idx] = item
        self.sort()

    def insert(self, idx, item):
        self._items.insert(idx, item)
        self.sort()

    def sort_by(self, *sort_keys):
        if sort_keys:
            self._items.sort(key=operator.attrgetter(*sort_keys))
