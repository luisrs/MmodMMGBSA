import re
from fatools.utils.validation.validator import FieldValidator


class FormatValidator(FieldValidator):
    """Validates whether the specified value has the correct form."""

    required_options = ('pattern',)
    err_template = "'{name}' does not match expected format"
    err_type_template = "'{name}' is not a string"

    def validate_field(self, name, value):
        try:
            if re.match(self.options['pattern'], value) is None:
                raise self._construct_error(name, value)
            return True
        except TypeError:
            raise self._construct_error(name, value, self.err_type_template)

    def _sanitize_options(self, options):
        options = super(FormatValidator, self)._sanitize_options(options)
        return options
