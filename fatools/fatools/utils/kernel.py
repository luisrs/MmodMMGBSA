import inspect
import re
import sys
from contextlib import contextmanager
from types import MethodType

from fatools.utils.inflection import underscore


# TODO add docstring
class FormattedError(Exception):
    def __init__(self, template=None, **kwargs):
        template = template or self.get_default_template()
        super(FormattedError, self).__init__(template.format(**kwargs))

    def get_default_template(self):
        try:
            return getattr(self, '__template__')
        except AttributeError:
            raise ValueError('missing required error template')


# TODO add docstring
class ArgumentError(FormattedError):
    pass


# TODO add docstring
class InvalidArgumentError(ArgumentError):
    __template__ = "invalid argument '{name}': {value}"

    def __init__(self, name, value, template=None, **kwargs):
        self.argname = kwargs['name'] = name
        self.argvalue = value
        kwargs['value'] = repr(value)
        super(InvalidArgumentError, self).__init__(template, **kwargs)


# TODO add docstring
class MissingArgumentError(ArgumentError):
    __template__ = "missing required '{name}' argument"

    def __init__(self, name, template=None, **kwargs):
        self.argname = kwargs['name'] = name
        super(MissingArgumentError, self).__init__(template, **kwargs)


# TODO add docstring
class InvalidTypeError(FormattedError):
    __template__ = "invalid value type {type}, expected {expected_type}"

    def __init__(self, expected_type, value, template=None, **kwargs):
        self.expected_type = expected_type
        self.value_type = value

        if isinstance(expected_type, (tuple, list)):
            kwargs['expected_type'] = tuple(map(clsname, expected_type))
        else:
            kwargs['expected_type'] = repr(clsname(expected_type))
        kwargs['type'] = repr(clsname(value))
        super(InvalidTypeError, self).__init__(template, **kwargs)


# TODO add docstring
class KeypathGetter(object):
    def __init__(self, *keys_and_idxs):
        if len(keys_and_idxs) == 1 and isinstance(keys_and_idxs[0], str):
            keys_and_idxs = KeypathGetter._parse_keypath(keys_and_idxs[0])
        self._items = tuple(keys_and_idxs)

    def __call__(self, obj):
        for key_or_idx in self._items:
            if isinstance(key_or_idx, int):
                obj = obj[key_or_idx]
                continue
            try:
                obj = getattr(obj, key_or_idx)
            except AttributeError:
                try:
                    obj = obj[key_or_idx]
                except (AttributeError, KeyError, TypeError):
                    # call again to raise original exception
                    getattr(obj, key_or_idx)
        return obj

    @staticmethod
    def _parse_keypath(keypath):
        items = []
        for item in re.split(r'\.|\[|\]\.?', keypath):
            if item == '':
                continue
            try:
                items.append(int(item))
            except ValueError:  # it a string
                if not re.match(r'^\w+$', item):
                    template = 'invalid keypath: {value}'
                    raise InvalidArgumentError('keypath', keypath, template)
                items.append(item)
        return items


# TODO add docstring
def ensure_type(dtype, value, converter=None):
    if dtype is None or isinstance(value, dtype):
        return value
    try:
        return converter(value)
    except (TypeError, ValueError):
        raise InvalidTypeError(dtype, value)


# TODO add docstring
def extend_class(cls, func_or_name=None, name=None):
    def wrap(func):
        cls_dict = _get_class_dict(cls)
        if callable(func):  # not a property
            func = MethodType(func, None, cls)  # convert to bound method
        cls_dict[name or func.__name__] = func
        return func
    if callable(func_or_name) or isinstance(func_or_name, property):
        return wrap(func_or_name)
    if name is None:
        name = func_or_name
    return wrap


def getattrnames(instance):
    """Return non-private instance attribute names."""
    return tuple(sorted([attr_name for attr_name in vars(instance).keys()
                         if not attr_name.startswith('_')]))


def getclassname(instance_or_cls):
    """Return class name.

    Examples
    --------
    >>> from fatools.utils.kernel import getclassname
    >>> getclassname(int)
    'int'
    >>> getclassname(10)
    'int'

    """
    return getclass(instance_or_cls).__name__
clsname = getclassname


def getclass(instance_or_cls):
    """Return the class object associated with the given object."""
    return instance_or_cls if inspect.isclass(instance_or_cls) \
        else instance_or_cls.__class__


def getqualifier(instance_or_cls, prefix='', suffix=''):
    """Generate and/or return a string qualifier for the given class.

    This function permits to generate a well-formatted string representation
    or *qualifier* of a class by removing specified namespace
    (e.g. FAMissingArgumentValidationError -> missing_argument).

    .. note:: Note that classes can declared a custom qualifier by setting the
              class attribute ``__qualifier__``, value that will be returned
              by this function when present.
              In such case, the `prefix` and `suffix` arguments are ignored.

    Parameters
    ----------
    instance_or_cls : any object
        Either an instance of class or the class object itself.
    prefix, suffix : str, optional
        Class name prefix and suffix, as part of the namespace, to be removed.
        Matching of both `prefix` and `suffix` is case-insensitive.
        Default to empty string (``''``).

    Returns
    -------
    str
        The class qualifier.

    Examples
    --------
    >>> from fatools.utils.kernel import getqual
    >>> getqual(type('Validator', (), {}))
    'validator'
    >>> getqual(type('PresenceValidator', (), {}), suffix='Validator')
    'presence'
    >>> getqual(type('PresenceValidator', (), {}), suffix='validator')
    'presence'
    >>> getqual(type('FAValidator', (), {}), prefix='fa')
    'validator'
    >>> getqual(int)
    'int'
    >>> cls = type('FAMissingArgumentValidationError', (), {})
    >>> getqual(cls, prefix='fa', suffix='ValidationError')
    'missing_argument'
    >>> getqual(cls())  # it also works with instances
    'missing_argument'
    >>> C = type('C', (), dict(__qualifier__='custom_qualifier'))
    >>> getqual(C)  # class has the special '__qualifier__' attribute
    'custom_qualifier'

    """
    cls = getclass(instance_or_cls)
    if not hasattr(cls, '__qualifier__'):
        pattern = r'(?i)^{}|{}$'.format(prefix, suffix)
        return underscore(re.sub(pattern, '', getclassname(cls)))
    return cls.__qualifier__
getqual = getqualifier


# TODO add docstring
# TODO add tests
def getter(*items):
    if len(items) == 1:
        return KeypathGetter(items[0])
    getters = tuple(map(KeypathGetter, items))
    return lambda obj: tuple(getter(obj) for getter in getters)


def isiterable(obj, classinfo=None, of_type=None):
    """Check if the `obj` argument conforms to the *iterable* interface.

    As the Python glossary states, an iterable object is capable of returning
    its members one at a time. Thus, any object that implements either the
    :meth:`__iter__` or :meth:`__getitem__` special methods is considered as
    iterable.

    Parameters
    ----------
    obj : object
        Any object.
    classinfo : type or tuple of type, optional
        If given, the `obj` argument must be an instance of the `classinfo`
        argument, or of a subclass thereof.
        Defaults to None (no check).
    of_type : type or tuple of type, optional
        If given, checks that all elements in the iterable are instances of the
        `of_type` argument, or of a subclass thereof.
        Defaults to None (no check).

    Returns
    -------
    bool
        True if the given object is an iterable that conforms to the given
        restrictions, otherwise returns False.

    Examples
    --------
    >>> from fatools.utils.kernel import isiterable
    >>> isiterable(['a', 'b'])
    True
    >>> isiterable(['a', 'b'], tuple)
    False
    >>> isiterable(['a', 'b'], (tuple, int))
    False
    >>> isiterable(['a', 'b'], (tuple, list))
    True
    >>> isiterable(['a', 'b'], of_type=str)
    True
    >>> isiterable(['a', 'b'], of_type=int)
    False
    >>> isiterable(['a', 'b'], of_type=(int, str))
    True
    >>> isiterable(['a', 'b', 1], of_type=(int, str))
    True
    >>> isiterable(['a', 'b', 1, 2.], of_type=(int, str))
    False

    """
    if classinfo is not None:
        if not isinstance(obj, classinfo):
            return False
    elif not hasattr(obj, '__iter__') and not hasattr(obj, '__getitem__'):
        return False
    if of_type is not None:
        return all(isinstance(ele, of_type) for ele in obj)
    return True


# TODO add docstring
@contextmanager
def redirect_stream(stdout=None, stderr=None, reset=False):
    original_streams = dict(stdout=sys.stdout, stderr=sys.stderr)
    if stdout is not None:
        sys.stdout = sys.__stdout__ if stdout == 'orig' else stdout
    if stderr is not None:
        sys.stderr = sys.__stderr__ if stderr == 'orig' else stderr
    yield
    sys.stdout = original_streams['stdout']
    sys.stderr = original_streams['stderr']


def reraise(err, msg, *args):
    """Short-hand for overriding Exception message.

    It replaces exception original arguments by the passed message,
    and re-raise it without lossing the original traceback.

    Parameters
    ----------
    err : Exception object
        A raised Exception object.
    msg : str
        Exception message to replace with.
    *args
        If given, ``str.format`` will be call on ``msg`` with the passed
        arguments.

    Examples
    --------
    >>> from fatools.utils.kernel import reraise
    >>> int('a')
    Traceback (most recent call last):
      ...
    ValueError: invalid literal for int() with base 10: 'a'
    >>> try:
    ...     a = int('a')
    ... except ValueError as err:
    ...     reraise(err, 'custom error')
    ...
    Traceback (most recent call last):
      ...
    ValueError: custom error

    """
    err.args = (msg.format(*args),)
    raise


@contextmanager
def suppress(*exceptions):
    """Suppress any of the specified exceptions if they occur.

    Return a context manager that suppresses any of the specified exceptions
    if they occur in the body of a with statement and then resumes execution
    with the first statement following the end of the with statement.

    Same as :meth:`contextlib.suppress` from Python 3.4.

    Examples
    --------
    >>> from fatools.utils.kernel import suppress
    >>> data = dict(key='value')
    >>> data['non-existent key']
    Traceback (most recent call last):
      ...
    KeyError: 'non-existent key'
    >>> with suppress(KeyError):
    ...     data['non-existent key']
    ...
    >>> # error was suppressed

    """
    try:
        yield
    except exceptions:
        pass


def _get_class_dict(cls):
    import ctypes as c

    _get_dict = c.pythonapi._PyObject_GetDictPtr
    _get_dict.restype = c.POINTER(c.py_object)
    _get_dict.argtypes = [c.py_object]
    return _get_dict(cls)[0]
