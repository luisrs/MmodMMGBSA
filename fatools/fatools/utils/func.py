import inspect
import sys
from abc import ABCMeta, abstractmethod
from collections import Mapping, MutableMapping

from fatools.utils.kernel import (ArgumentError, InvalidArgumentError,
                                  MissingArgumentError, getqualifier, getter,
                                  isiterable)


# TODO add reject function
# TODO add check function that receives an argument and predicate,
#      raising an ArgumentError is the argument is invalid


class NotFoundError(Exception):
    """Raised by the :func:`find` function when no element is found."""
    pass


class Predicate(object):
    """Abstract class that predicate classes must inherit from.

    A predicate object is a functional (callable) form of a logical condition,
    thus being useful to filter an iterable object, for example::

        predicate = Predicate(...)
        result = filter(predicate, iterable)

    Note that the result of calling a predicate is always a boolean,
    and no exceptions must be raised during evaluation.

    """
    __metaclass__ = ABCMeta

    def __and__(self, other):
        return CompoundPredicate(self, other, operator=all)

    @abstractmethod
    def __call__(self, obj):
        """Return True if `obj` satisfies the condition, False otherwise."""
        return NotImplemented

    def __or__(self, other):
        return CompoundPredicate(self, other, operator=any)


class CompoundPredicate(Predicate):
    """Represent logical "gate" operations (AND/OR) between predicates.

    A compound predicate with one or more subpredicates evaluates to the truth
    of all of its subpredicates by default. This can be changed by setting the
    :attr:`operator` attribute to the :func:`any` builtin function.

    .. note:: This class is not intended to be instantiated directly but rather
              use logical operators (| or &) on predicate objects to create a
              compound predicate.

    """
    def __init__(self, *args, **kwargs):
        self.operator = extract(kwargs, 'operator', default=all)
        named_predicates = tuple(_create_predicate(name, kwargs[name])
                                 for name in kwargs)
        self.subpredicates = args + named_predicates
        if not self.subpredicates:
            raise MissingArgumentError(None, 'expected at least one predicate')

    def __call__(self, obj):
        return self.operator(pd(obj) for pd in self.subpredicates)


class AttributePredicate(Predicate):
    """Check that instance attributes have the specified values.

    If an attribute does not exist, :exc:`AttributeError` exception will be
    suppressed and False will be returned instead.

    Examples
    --------
    >>> import argparse
    >>> from fatools.utils.func import AttributePredicate
    >>> predicate = AttributePredicate(attr1=1, attr2='two')
    >>> predicate(argparse.Namespace(attr1=1, attr2='two'))
    True
    >>> predicate(argparse.Namespace(attr1=1, attr2=2))
    False
    >>> predicate(argparse.Namespace(attr1=1))  # does not have attr2
    False

    """
    def __init__(self, **attributes):
        self.items = tuple(attributes.items())

    def __call__(self, obj):
        try:
            return all(getattr(obj, attr) == val for attr, val in self.items)
        except AttributeError:
            return False


class InclusionPredicate(Predicate):
    """Check that an object is contained by the given container.

    Examples
    --------
    >>> from fatools.utils.func import InclusionPredicate
    >>> predicate = InclusionPredicate('0123456789')
    >>> predicate('0')
    True
    >>> predicate('a')
    False
    >>> predicate(0)
    False

    """
    def __init__(self, items):
        self.items = items

    def __call__(self, obj):
        try:
            return obj in self.items
        except TypeError:
            return False


class ExclusionPredicate(InclusionPredicate):
    """Check that an object is not contained by the given container.

    Examples
    --------
    >>> from fatools.utils.func import ExclusionPredicate
    >>> predicate = ExclusionPredicate('0123456789')
    >>> predicate('0')
    False
    >>> predicate('a')
    True
    >>> predicate(0)
    True

    """
    def __call__(self, obj):
        return not super(ExclusionPredicate, self).__call__(obj)


def compact(iterable):
    """Return all non-None elements from ``iterable``."""
    return exclude(iterable, (None,))


def find(iterable, *predicates, **kwargs):
    """Return the first element that satisfies the given predicates.

    This function expects one or more predicate objects to search for the
    element of interest (see :class:`Predicate` class for a description
    of a "predicate").
    Note that when two or more predicates are given, an element must fulfill
    all conditions to be selected and returned.

    Parameters
    ----------
    iterable : iterable object
        Can be either a sequence, a container which supports iteration,
        or an iterator.
    \*predicate : callable object
        One or more :class:`Predicate` or callable objects that accepts one
        argument and returns True for the element to be selected.
    \*\*kwargs
        A series of keyword arguments where each key corresponds to a predicate
        name or alias, and the associated value is the argument passed to
        the corresponding predicate constructor.
        See the :mod:`~fatools.utils.func` module documentation for a list of
        available predicate aliases.
    default : any object, optional
        Value returned when no element is found.
        Defaults to None.
    silent : bool, optional
        If False, this function raises a :exc:`NotFoundError` exception rather
        than returning `default` value.
        Defaults to True.

    Returns
    -------
    object
        Either the found object, if any, or the default value (defaults to
        None) otherwise.

    Raises
    ------
    ValueError
        If no predicate is passed, that is, ``find(iterable)``,
        or if an unknown predicate name is given.
    NotFoundError
        If no object is found and `silent` is False (defaults to True).

    See also
    --------
    select : return all elements that satisfy the given predicates rather
             than only the first one.
    reject : complementary function that returns elements that do not satisfy
             the given predicates.

    Examples
    --------
    >>> from fatools.utils.func import find
    >>> find('abc', lambda ele: ele == 'a')
    'a'
    >>> find('abc', within='bc')  # named predicate
    'b'
    >>> find('abc', within='d')  # default is None
    >>> find('abc', within='d', default=-1)
    -1
    >>> find('abc', within='d', silent=False)
    Traceback (most recent call last):
      ...
    fatools.utils.func.NotFoundError: no element satisfied the given predicates

    If no predicate object or an unknown predicate name is given,
    a :exc:`ValueError` exception will be raised.

    >>> find('abc')
    Traceback (most recent call last):
      ...
    ValueError: expected at least one predicate
    >>> find('abc',  unknown_predicate='...')
    Traceback (most recent call last):
      ...
    ValueError: unknown predicate 'unknown_predicate'

    """
    update_dict(kwargs, dict(operator=all))
    options = extract(kwargs, ('default', 'silent'))
    predicate = CompoundPredicate(*predicates, **kwargs)
    for ele in iterable:
        if predicate(ele):
            return ele
    if not options.get('silent', True):
        raise NotFoundError('no element satisfied the given predicates')
    return options.get('default', None)


# TODO add docstring
def flatten(iterable):
    memo = []
    for ele in iterable:
        if isinstance(ele, (list, tuple)):
            memo.extend(flatten(ele))
        else:
            memo.append(ele)
    return memo


# TODO add complete docstring
# TODO add tests
def exclude(iterable, items, key=None):
    """Return all those elements that are not contained by ``items``."""
    if key is None:
        key = itself
    elif isinstance(key, (int, str)):
        key = getter(key)
    if not isinstance(items, (list, tuple)):
        items = (items,)
    return reject(iterable, lambda obj: key(obj) in items)


def extract(mapping, keys_or_predicate, default=None, delete=True):
    """Extract requested entries from a dictionary.

    Parameters
    ----------
    mapping : dict
        A dictionary or mapping object.
    keys_or_predicate : str or tuple of str or callable object
        One (it may be a single string) or more keys to be extracted. If a
        callable object is given, it will be called for each key-value pair,
        and must return either True for those entries to be extracted, or
        False otherwise.
    default : any object, optional
        Value returned if the given key is not in `mapping`.
        Only works when `keys_or_predicate` is a key string.
        Defaults to None, so that this method never raises a :exc:`KeyError`
        exception.
    delete : bool, optional
        Whether to delete entry from `mapping` argument or not.
        Default to True.

    Returns
    -------
    object or dict
        Either the value associated with the given key if exists or else
        `default`, or a dictionary with the requested entries.

        Note that a dictionary will be returned if `keys_or_predicate` is
        either a tuple or list, or a callable object, regardless of whether
        `keys_or_predicate` or the resulting dictionary has a single element.

    Raises
    ------
    TypeError
        If `mapping` argument is an invalid mapping object.

    Examples
    --------
    >>> from fatools.utils.func import extract
    >>> cfg = dict(cpu=8, host='localhost', njobs=1, tpp=2, local=True,
    ...            max_retries=2, debug=False)
    >>> extract(cfg, 'njobs')
    1
    >>> cfg
    {'host': 'localhost', 'tpp': 2, 'debug': False, 'local': True, \
'max_retries': 2, 'cpu': 8}
    >>> extract(cfg, ('max_retries',))
    {'max_retries': 2}
    >>> cfg
    {'host': 'localhost', 'tpp': 2, 'debug': False, 'local': True, 'cpu': 8}
    >>> extract(cfg, 'cmd', default='desmond')
    'desmond'
    >>> extract(cfg, ('cpu', 'host'))
    {'host': 'localhost', 'cpu': 8}
    >>> cfg
    {'debug': False, 'local': True, 'tpp': 2}
    >>> extract(cfg, lambda _, v: isinstance(v, bool))
    {'debug': False, 'local': True}
    >>> cfg
    {'tpp': 2}
    >>> extract(cfg, ('cpu', 'tpp'), delete=False)
    {'tpp': 2}
    >>> cfg
    {'tpp': 2}

    """
    def extract_key(key):
        value = mapping.get(key, default)
        if key in mapping and delete is True:
            del mapping[key]
        return value

    def extract_with_predicate(predicate):
        data = dict()
        for key, val in tuple(mapping.items()):
            if predicate(key, val):
                data[key] = val
                if delete:
                    del mapping[key]
        return data

    if not isinstance(mapping, MutableMapping if delete else Mapping):
        raise InvalidArgumentError('mapping', mapping)
    if callable(keys_or_predicate):
        return extract_with_predicate(keys_or_predicate)
    if isiterable(keys_or_predicate, (tuple, list)):
        return extract_with_predicate(lambda key, _: key in keys_or_predicate)
    return extract_key(keys_or_predicate)  # one key as str


def itself(obj):
    """Functional form to return the same object."""
    return obj


# TODO add tests
def reject(iterable, predicate):
    """Return all but those elements that satisfy the given predicate."""
    return [ele for ele in iterable if not predicate(ele)]


def select(iterable, *predicates, **kwargs):
    """Return those elements of `iterable` that satisfy the given predicates.

    This function expects one or more predicate objects to filter out
    the elements of interest (see :class:`Predicate` class for a description
    of a "predicate").
    Note that when two or more predicates are given, elements must fulfill all
    conditions to be selected and returned.

    Parameters
    ----------
    iterable : iterable object
        It may be either a sequence, a container which supports iteration,
        or an iterator.
    \*predicates
        One or more Predicate or callable objects that accepts one argument
        and returns True for those elements to be selected.
    \*\*kwargs
        A series of keyword arguments where each key corresponds to a predicate
        name or alias, and the associated value is the argument passed to
        the corresponding predicate constructor.
        See the :mod:`~fatools.utils.func` module documentation for a list of
        available predicate aliases.

    Returns
    -------
    tuple
        A tuple with the selected elements; empty if no elements satisfied
        the given conditions.

    Raises
    ------
    ValueError
        If no predicate is passed, that is, ``select(iterable)``,
        or if an unknown predicate name is given.

    See also
    --------
    find : return the first selected element instead of a list.
    reject : complementary function that returns elements that do not satisfy
             the given predicates.

    Examples
    --------
    >>> from fatools.utils.func import select
    >>> select('abc', lambda ele: ele in 'ab')
    ('a', 'b')
    >>> select('abc', lambda ele: ele == 'd')
    ()
    >>> select('abc', not_in='ab')  # named predicate
    ('c',)

    If no predicate object or an unknown predicate name is given,
    a :exc:`ValueError` exception will be raised.

    >>> select('abc')
    Traceback (most recent call last):
      ...
    ValueError: expected at least one predicate
    >>> select('abc',  unknown_predicate='...')
    Traceback (most recent call last):
      ...
    ValueError: unknown predicate 'unknown_predicate'

    """
    update_dict(kwargs, dict(operator=all))
    predicate = CompoundPredicate(*predicates, **kwargs)
    return tuple(filter(predicate, iterable))


def transform_values(mapping, func, copy=False):
    """Convert all values of a mapping object using callable ``func``.

    Parameters
    ----------
    mapping : dict
        A dictionary or mapping object to be changed.
    func : callable object
        A function or callable object that takes one value and return a
        transformed version.
    copy : bool, optional
        If True, a copy of `mapping` argument will be updated and returned
        instead, keeping `mapping` intact.
        Default to False.

    Returns
    -------
    dict
        Updated dictionary regardless of whether ``copy`` is False.

    Examples
    --------
    >>> from fatools.utils.func import transform_values
    >>> cfg = dict(cpu=1, host='localhost', debug=False)
    >>> cfg
    {'debug': False, 'host': 'localhost', 'cpu': 1}
    >>> transform_values(cfg, str)
    {'debug': 'False', 'host': 'localhost', 'cpu': '1'}
    >>> cfg
    {'debug': 'False', 'host': 'localhost', 'cpu': '1'}

    By default, this function make transformations in-place,
    but setting ``copy`` to True generates a copy of ``mapping``:

    >>> cfg = dict(cpu=1, host='localhost', debug=False)
    >>> transform_values(cfg, str, copy=True)
    {'debug': 'False', 'host': 'localhost', 'cpu': '1'}
    >>> cfg
    {'debug': False, 'host': 'localhost', 'cpu': 1}

    """
    if copy is True:
        mapping = mapping.copy()
    for key in mapping:
        mapping[key] = func(mapping[key])
    return mapping


def update_dict(mapping, other, copy=False, override=True):
    """Update and return a dict with given entries.

    Parameters
    ----------
    mapping : dict
        A dictionary or mapping object to be updated.
    other : dict
        A dictionary with entries to set.
    copy : bool, optional
        If True, a copy of `mapping` argument will be updated and returned
        instead, keeping `mapping` intact.
        Default to False.
    override : bool, optional
        If True, existing entries in `mapping` argument will be kept intact
        even if they appear in the `other` argument, otherwise they will be
        overridden.
        Defaults to True.

    Returns
    -------
    dict
        Updated dictionary.

    Examples
    --------
    >>> from fatools.utils.func import update_dict
    >>> cfg = dict(cpu=1, host='localhost', debug=False)
    >>> cfg
    {'debug': False, 'host': 'localhost', 'cpu': 1}
    >>> update_dict(cfg, dict(cpu=10, host='anton', tpp=4))
    {'debug': False, 'host': 'anton', 'cpu': 10, 'tpp': 4}
    >>> cfg
    {'debug': False, 'host': 'anton', 'cpu': 10, 'tpp': 4}
    >>> update_dict(cfg, dict(cpu=1000, tpp=2), copy=True)
    {'debug': False, 'host': 'anton', 'cpu': 1000, 'tpp': 2}
    >>> cfg
    {'debug': False, 'host': 'anton', 'cpu': 10, 'tpp': 4}
    >>> update_dict(cfg, dict(cpu=1000, tpp=2), override=False)
    {'debug': False, 'host': 'anton', 'cpu': 10, 'tpp': 4}

    """
    if copy is True:
        mapping = mapping.copy()
    for key in other.keys():
        if key in mapping and override is False:
            continue
        mapping[key] = other[key]
    return mapping


def _create_predicate(name, arg):
    try:
        return _predicate_registry[name](arg)
    except KeyError:
        raise ArgumentError('unknown predicate {name}', name=repr(name))


def _register_predicate_alias(predicate_class, alias):
    if alias in _predicate_registry:
        raise ArgumentError('predicate alias {} is already registered',
                            repr(alias))
    _predicate_registry[alias] = predicate_class


def _setup_predicate_registry():
    self = sys.modules[__name__]
    classes = [cls for _, cls in inspect.getmembers(self, inspect.isclass)]
    cond = lambda cls: issubclass(cls, Predicate) and cls is not Predicate
    predicate_classes = filter(cond, classes)

    registry = {}
    for predicate_class in predicate_classes:
        name = getqualifier(predicate_class, suffix='predicate')
        registry[name] = predicate_class
    return registry

_predicate_registry = _setup_predicate_registry()
_register_predicate_alias(InclusionPredicate, 'within')
_register_predicate_alias(ExclusionPredicate, 'not_in')
