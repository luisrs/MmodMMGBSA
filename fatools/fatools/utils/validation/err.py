"""Collection of validation errors."""
from fatools.utils.func import update_dict
from fatools.utils.kernel import FormattedError


class ValidationError(FormattedError):
    pass


class OptionValidationError(ValidationError):
    template_prefix = '{validator} validator: '

    def __init__(self, validator, name, template=None, **kwargs):
        template = template or self.get_default_template()
        info = dict(option=name, validator=str(validator))
        update_dict(kwargs, info, override=False)
        super(OptionValidationError, self).__init__(
            self.template_prefix + template, **kwargs)


class MissingOptionValidationError(OptionValidationError):
    __template__ = "missing required '{option}' option"
