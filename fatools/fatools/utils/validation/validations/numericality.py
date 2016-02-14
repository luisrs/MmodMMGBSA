import numbers
import operator
from fatools.utils.func import extract, update_dict
from fatools.utils.validation.err import OptionValidationError
from fatools.utils.validation.validator import FieldValidator

_available_checks = dict(
    greater_than=operator.gt,
    greater_than_or_equal_to=operator.ge,
    less_than=operator.lt,
    less_than_or_equal_to=operator.le,
    equal_to=operator.eq,
    other_than=operator.ne,
    odd=lambda n: n % 2 != 0,
    even=lambda n: n % 2 == 0,
    only_integer=lambda n: isinstance(n, int))

_check_aliases = dict(
    gt='greater_than',
    ge='greater_than_or_equal_to',
    lt='less_than',
    le='less_than_or_equal_to',
    eq='equal_to',
    ne='other_than')

_err_templates = dict(
    not_a_number="'{name}' is not a number",
    greater_than="'{name}' is less than or equal to {option_value}",
    greater_than_or_equal_to="'{name}' is less than {option_value}",
    less_than="'{name}' is greater than or equal to {option_value}",
    less_than_or_equal_to="'{name}' is greater than {option_value}",
    equal_to="'{name}' is not equal to {option_value}",
    other_than="'{name}' is equal to {option_value}",
    odd="'{name}' is not odd",
    even="'{name}' is not even",
    only_integer="'{name}' is not an integer")


# TODO add docstring
class NumericalityValidator(FieldValidator):
    acceptable_options = tuple(_available_checks) + tuple(_check_aliases)

    def validate_field(self, name, value):
        if not isinstance(value, numbers.Number):
            raise self._construct_error(name, value, 'not_a_number')

        checks = extract(self.options, _available_checks.keys(), delete=False)
        for option, option_value in checks.items():
            predicate = _get_numericality_predicate(option, option_value)
            if not predicate(value):
                raise self._construct_error(name, value, option, option_value)
        return True

    def _construct_error(self, name, value, option, option_value=None):
        return super(NumericalityValidator, self)._construct_error(
            name, value, _err_templates[option], option_value=option_value)

    def _sanitize_options(self, options):
        options = super(NumericalityValidator, self)._sanitize_options(options)

        check_keys = tuple(_available_checks) + tuple(_check_aliases)
        for name, value in extract(options, check_keys, delete=False).items():
            if name in _check_aliases:
                del options[name]
                name = _check_aliases[name]
                options[name] = value

            if name in ('odd', 'even', 'only_integer') and value is not True:
                del options[name]
                continue

            if not isinstance(value, numbers.Number):
                template = "'{option}' option must be a number"
                raise OptionValidationError(self, name, template)
        return options


def _get_numericality_predicate(option, value):
    if option in ('odd', 'even', 'only_integer'):
        return _available_checks[option]
    return lambda a: _available_checks[option](a, value)
