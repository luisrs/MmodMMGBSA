import inspect
from fatools.utils.caching import cached_property
from fatools.utils.kernel import clsname, isiterable
from fatools.utils.text import to_sentence
from fatools.utils.validation.validator import FieldValidator
from fatools.utils.validation.err import OptionValidationError


# TODO move type checking functionality to TypePredicate
class TypeValidator(FieldValidator):
    """Validates that the specified field is an instance of given type."""

    required_options = ('dtype',)

    dtype = property(lambda self: self.options['dtype'])
    err_template = ("invalid value for '{name}', expected {dtype} type, "
                    "got {value} ({value_type})")

    @cached_property
    def type_annotation(self):
        return to_sentence(self.dtype, two_words_sep=' or ',
                           last_word_sep=' or ',
                           converter=clsname)

    def validate_field(self, name, value):
        if not isinstance(value, self.dtype):
            raise self._construct_error(name, value)
        return True

    def _sanitize_options(self, options):
        options = super(TypeValidator, self)._sanitize_options(options)

        dtype = options['dtype']
        if not isiterable(dtype, (tuple, list)):
            options['dtype'] = dtype = (dtype,)
        if not all(inspect.isclass(dtype) for dtype in dtype):
            template = 'expected a tuple of classes, got {value}'
            raise OptionValidationError(
                self, 'dtype', template, value=dtype)
        return options

    def _construct_error(self, name, value, **kwargs):
        return super(TypeValidator, self)._construct_error(
            name, value, dtype=self.type_annotation, value_type=clsname(value))
