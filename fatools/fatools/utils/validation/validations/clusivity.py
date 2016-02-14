from collections import Container
from fatools.utils.validation.err import OptionValidationError
from fatools.utils.validation.validator import FieldValidator


class _ClusivityValidator(FieldValidator):
    predicate = NotImplemented
    required_options = ('choices',)

    choices = property(lambda self: self.options['choices'])

    def _sanitize_options(self, options):
        options = super(_ClusivityValidator, self)._sanitize_options(options)

        choices = options.get('choices', None)
        if not isinstance(choices, Container):
            template = ("A non-empty container object is required, "
                        "and must be supplied as the 'choices' option, "
                        "got: {choices}")
            raise OptionValidationError(self, 'choices', template)
        return options


class InclusionValidator(_ClusivityValidator):
    """Validates if the value of the specified field is in an iterable."""

    err_template = "value for '{name}' must be one of {choices}, got {value}"

    def validate_field(self, name, value):
        if value not in self.choices:
            raise self._construct_error(name, value)
        return True


class ExclusionValidator(_ClusivityValidator):
    """Validates if the value of the specified field is not in an iterable."""

    err_template = "value for '{name}' must not be one of {choices}, got {value}"

    def validate_field(self, name, value):
        if value in self.choices:
            raise self._construct_error(name, value)
        return True
