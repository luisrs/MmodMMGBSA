from abc import ABCMeta, abstractmethod
from fatools.utils.func import find, extract, update_dict
from fatools.utils.kernel import getqualifier
from fatools.utils.validation.err import (
    MissingOptionValidationError, ValidationError)


def get_validator_kind(validator):
    return getqualifier(validator, suffix='validator')


class _ValidatorMeta(ABCMeta):
    def __new__(mcs, name, bases, namespace):
        cls = type.__new__(mcs, name, bases, namespace)
        cls.acceptable_options = cls._gather_acceptable_options()
        if 'kind' not in namespace:  # does not declare its own kind
            cls.kind = get_validator_kind(cls)
        return cls

    def _gather_acceptable_options(cls):
        """Collect all accepted options, including those declared by super."""
        accepted_options = []
        for sentinel in cls.__mro__[:-2]:  # last item would be object
            accepted_options.extend(sentinel.acceptable_options)
            accepted_options.extend(sentinel.required_options)
            accepted_options.extend(sentinel.default_options.keys())
        return tuple(sorted(set(accepted_options)))


# TODO Added conditional options ('if', 'unless')
class Validator(object):
    __metaclass__ = _ValidatorMeta

    default_options = dict()
    required_options = ()
    acceptable_options = ()

    def __init__(self, **options):
        update_dict(options, self.default_options, override=False)
        options = extract(options, self.acceptable_options)
        self._options = self._sanitize_options(options)
    options = opts = property(lambda self: self._options)

    def __call__(self, *args, **kwargs):
        return self.validate(*args, **kwargs)

    def __str__(self):
        try:
            return self.kind
        except AttributeError:
            return get_validator_kind(self)

    @abstractmethod
    def validate(self, *args, **kwargs):
        return NotImplemented

    def _construct_error(self, template, **kwargs):
        return ValidationError(template, **kwargs)

    def _sanitize_options(self, options):
        predicate = lambda option: option not in options
        missing_option = find(self.required_options, predicate)
        if missing_option:
            raise MissingOptionValidationError(self, missing_option)
        return options


class FieldValidator(Validator):
    default_options = dict(allow_none=False)
    err_template = "invalid value for field '{name}', got {value}"

    def should_validate(self, value):
        return value is not None or not self.options['allow_none']

    def validate(self, name, value, silent=False):
        if not self.should_validate(value):
            return True
        try:
            return self.validate_field(name, value)
        except ValidationError as err:
            if silent:
                return False
            raise err

    @abstractmethod
    def validate_field(self, name, value):
        return NotImplemented

    def _construct_error(self, name, value, template=None, **kwargs):
        info = dict(name=name, value=repr(value))
        update_dict(kwargs, info, override=False)
        update_dict(kwargs, self.options, override=False)
        return super(FieldValidator, self)._construct_error(
            template or self.err_template, **kwargs)
