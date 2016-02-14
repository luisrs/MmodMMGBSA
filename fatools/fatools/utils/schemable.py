from abc import ABCMeta
from operator import attrgetter

from fatools.utils.func import extract, update_dict, transform_values
from fatools.utils.kernel import (
    MissingArgumentError, clsname, suppress)
from fatools.utils.inflection import pluralize
from fatools.utils.mass_assign import MassAssignable
from fatools.utils.text import to_sentence
from fatools.utils.validation import (
    PresenceValidator, ValidationOptionParser)


class AbstractField(object):
    __metaclass__ = ABCMeta


# TODO add docstring
class FieldInfo(AbstractField):
    def __init__(self, allow_none=False, default=None, converter=None,
                 **validations):
        self.allow_none = allow_none
        self.converter = converter

        self._validators = ValidationOptionParser.parse(validations)
        if default is None:
            self._validators = self._validators + (PresenceValidator(),)
        else:
            self.default = default
        self._override_validation_options(allow_none=allow_none)

    def convert(self, value):
        if callable(self.converter):
            try:
                return self.converter(value)
            except (TypeError, ValueError):
                return value
        return value

    def validate(self, name, value, silent=False):
        return all(validator(name, value, silent=silent)
                   for validator in self._validators)

    def _override_validation_options(self, **options):
        for validator in self._validators:
            update_dict(validator._options, options)


# TODO improve docstring
class Schemable(type):
    """Metaclass that provides an interface to declare a class as an schema.

    An schema is represented as a class that contains a set of fields
    (instance attributes that can have metadata such validation rules),
    which are declared in the class body itself.
    This permits to have a clean declaration block, where instance variables
    are explicitly stated at the top of the class implementation.

    Such implementation relies heavily on the :class:`MassAssignable` mixin,
    which allows to assign instance attributes from keyword arguments given to
    the class constructor dynamically.

    Examples
    --------
    In the following example, ``Cmd`` fields are declared in the class body
    rather than in the :meth:`__init__` method, as it may be expected.

    >>> class Cmd(object):
    ...     __metaclass__ = Schemable
    ...     cpu = FieldInfo(alias='-cpu', dtype=int, default=1,
    ...                     predicate=lambda n: n > 0)
    ...     host = FieldInfo(alias='-host', default='localhost')
    ...     threads_per_core = FieldInfo(alias='-TPP', dtype=int, default=1,
    ...                                  predicate=lambda n: 0 < n < 4)
    ...
    >>> Cmd(cpu=8)
    Cmd(cpu=8, host='localhost', threads_per_core=1)

    In this case, :class:`FieldInfo` class is used to hold field metadata,
    but it may be any custom class as long as it has an :attr:`__field__`
    attribute set to True.
    Note that the `host` and `threads_per_core` fields have a default value,
    which is used to populate the instance in case they are missing as in the
    example above.

    """
    def __new__(cls, name, bases, namespace):
        fields = Schemable._gather_fields(bases, namespace)
        instance = type.__new__(cls, name, bases, namespace)
        instance._fields = fields
        instance.assignable_attributes = tuple(fields.keys())
        return instance

    def __call__(cls, *args, **kwargs):
        if not cls._fields:
            raise TypeError('cannot instantiate class {} with an empty schema'
                            .format(cls.__name__))
        update_dict(kwargs, Schemable._default_values(cls), override=False)
        return super(Schemable, cls).__call__(*args, **kwargs)

    def get_field_info(cls, name):
        """Return field infor for the given name."""
        try:
            return cls._fields[name]
        except KeyError:
            # TODO replace by custom error
            raise ValueError('unknown field: {}'.format(repr(name)))

    @staticmethod
    def _default_values(cls):
        """Return fields with their default value, if any, as a dict."""
        predicate = lambda _, fi: getattr(fi, 'default', None) is not None
        default_fields = extract(cls._fields, predicate, delete=False)
        transform_values(default_fields, attrgetter('default'))
        for field, _ in Schemable._noneable_fields(cls).items():
            default_fields[field] = None
        return default_fields

    @staticmethod
    def _extract_fields(namespace):
        """Return fields declared in the class body or namespace."""
        predicate = lambda _, val: isinstance(val, AbstractField)
        return extract(namespace, predicate, delete=False)

    @staticmethod
    def _gather_fields(bases, namespace):
        """Return all fields including those declared by base classes."""
        fields = Schemable._extract_fields(namespace)
        for base in bases:
            with suppress(AttributeError):  # _fields variable may not exist
                update_dict(fields, base._fields, override=False)
        return fields

    @staticmethod
    def _noneable_fields(cls):
        """Return fields that are noneable (i.e., allow_none=True)."""
        predicate = lambda _, fi: getattr(fi, 'allow_none', False)
        return extract(cls._fields, predicate, delete=False)


# TODO add docstring
class Schema(MassAssignable):
    __metaclass__ = Schemable

    def __init__(self, **kwargs):
        super(Schema, self).__init__(**kwargs)
        self._check_for_missing_fields(kwargs.keys())
        self._after_initialize()

    def __setattr__(self, key, value):
        if key in self._fields:
            field_info = self._fields[key]
            value = field_info.convert(value)
            field_info.validate(key, value)
        super(Schema, self).__setattr__(key, value)

    def _after_initialize(self):
        pass

    def _check_for_missing_fields(self, passed_keys):
        missing_keys = sorted(set(self._fields) - set(passed_keys))
        required_keys = [key for key in missing_keys
                         if not self._fields[key].allow_none]
        if required_keys:
            count = len(required_keys)
            raise MissingArgumentError(
                missing_keys[0],
                '{cls}() missing {count} required {label}: {fields}',
                cls=clsname(self),
                count=count,
                label=pluralize('field', count),
                fields=to_sentence(map(repr, required_keys)))
