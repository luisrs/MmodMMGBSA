from fatools.utils.validation.validator import FieldValidator


class PresenceValidator(FieldValidator):
    """Validates that the specified field is present (not None)."""

    err_template = "'{name}' is missing"

    def validate_field(self, name, value):
        if value is None:
            raise self._construct_error(name, value)
        return True
