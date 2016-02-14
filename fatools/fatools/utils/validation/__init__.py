import inspect
import sys
from collections import Mapping
from fatools.utils.kernel import clsname
from fatools.utils.validation.err import (
    OptionValidationError, MissingOptionValidationError, ValidationError)
from fatools.utils.validation.optparse import ValidationOptionParser
from fatools.utils.validation.validations import (
    ExclusionValidator, FormatValidator, InclusionValidator,
    NumericalityValidator, PresenceValidator, PredicateValidator,
    TypeValidator)
from fatools.utils.validation.validator import FieldValidator, Validator


class _ValidatorRegistry(Mapping):
    _validators = dict()

    def __init__(self):
        self.__class__._gather_validators()

    def __getitem__(self, item):
        return self._validators[item]

    def __iter__(self):
        return iter(self._validators)

    def __len__(self):
        return len(self._validators)

    def register_validator(self, cls, aliases=()):
        self._validators[cls.kind] = cls
        for alias in aliases:
            self._validators[alias] = cls

    @classmethod
    def _gather_validators(cls):
        module = sys.modules[__name__]
        classes = inspect.getmembers(module, inspect.isclass)
        validator_classes = [clsobj for clsname, clsobj in classes
                             if clsname.endswith('Validator')]
        for validator_class in validator_classes:
            cls._validators[validator_class.kind] = validator_class
validators = _ValidatorRegistry()

# add some aliases
validators.register_validator(InclusionValidator, aliases=('within',))
validators.register_validator(ExclusionValidator, aliases=('not_in',))
