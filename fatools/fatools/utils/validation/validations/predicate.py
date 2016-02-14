from fatools.utils.validation.err import OptionValidationError
from fatools.utils.validation.validator import FieldValidator


class PredicateValidator(FieldValidator):
    """Validates whether the specified value has the correct form."""

    required_options = ('predicate',)

    def validate_field(self, name, value):
        if not self.options['predicate'](value):
            raise self._construct_error(name, value)
        return True

    def _sanitize_options(self, options):
        options = super(PredicateValidator, self)._sanitize_options(options)

        predicate = options['predicate']
        if not callable(predicate):
            template = 'expected a callable object'
            raise OptionValidationError(self, 'predicate', template)
        return options

