from itertools import groupby

from fatools.utils.kernel import getter, extend_class, isiterable
from fatools.utils.func import compact, exclude, flatten, transform_values


@extend_class(dict, name='transform_values')
def _dict_transform_values(self, func, copy=False):
    return transform_values(self, func, copy)


def extend_list():
    _extend_iterable(list)

    # TODO add examples
    # TODO add tests
    @extend_class(list, name='with_capacity')
    @classmethod
    def _list_with_capacity(cls, rows, cols=None, repeated_value=None):
        """Return an "empty" list with the given shape.

        Parameters
        ----------
        rows : int
            List capacity/length, or number of rows if a two-dimensional
            list is requested.
        cols : int, optional
            Number of columns. If given, a two-dimensional list will be
            returned. Defaults to None.
        repeated_value : None, optional
            Value used to fill the generated list. Defaults to None.

        """
        if cols is not None:
            return cls(cls(repeated_value for _ in range(cols))
                       for _ in range(rows))
        return cls(repeated_value for _ in range(rows))

    @extend_class(list, name='with_zeros')
    @classmethod
    def _list_with_zeros(cls, rows, cols=None):
        """Return list filled with zeros with the given shape.

        Shorthand for ``list.with_capacity(rows, cols, repeated_value=0)``.

        """
        return cls.with_capacity(rows, cols, repeated_value=0)


def extend_tuple():
    _extend_iterable(tuple)


def _extend_iterable(cls):
    @extend_class(cls, name='compact')
    def _iterable_compact(self):
        return cls(compact(self))

    @extend_class(cls, name='exclude')
    def _iterable_exclude(self, items, key=None):
        return cls(exclude(self, items, key))

    @extend_class(cls, name='pluck')
    def _iterable_pluck(self, *attrs):
        return tuple(map(getter(*attrs), self))

    @extend_class(cls, name='flatten')
    def _iterable_flatten(self):
        return cls(flatten(self))

    @extend_class(cls, name='freeze')
    def _iterable_freeze(self):
        return tuple(self)

    @extend_class(cls, name='group_by')
    def _iterable_group_by(self, key, *more_keys):
        if isinstance(key, (str, int)):
            if more_keys:
                key = getter(key, *more_keys)
            else:
                key = getter(key)
        elif isiterable(key, of_type=(str, int)):
            key = getter(*key)
        return cls((key, cls(group))
                   for key, group in groupby(self.sorted(key), key))

    @extend_class(cls, name='map')
    def _iterable_map(self, func):
        return cls(map(func, self))

    @extend_class(cls, name='map_with_index')
    def _iterable_map_with_index(self, func):
        return cls(func(i, ele) for i, ele in enumerate(self))

    @extend_class(cls, name='sorted')
    def _iterable_sorted(self, key=None, cmp=None, reverse=False):
        if isinstance(key, str):
            key = getter(key)
        elif isiterable(key, of_type=(str, int)):
            key = getter(*key)
        return cls(sorted(self, cmp=cmp, key=key, reverse=reverse))

    @extend_class(cls, name='sorted_by')
    def _iterable_sorted_by(self, *keys, **kwargs):
        return self.sorted(key=keys, reverse=kwargs.get('reverse', False))

    @extend_class(cls, name='uniq')
    def _iterable_uniq(self):
        return cls(set(self)).sorted(key=self.index)
