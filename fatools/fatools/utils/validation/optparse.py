import sys
from fatools.utils.func import select, update_dict
from fatools.utils.kernel import ArgumentError

validation = sys.modules['fatools.utils.validation']  # avoid circular import


# TODO add full docstring
class ValidationOptionParser(object):
    """Gather validator options and create validator objects with them."""

    @classmethod
    def parse(cls, options):
        validator_option_list = cls._extract_validator_class_and_options(options)
        options = cls._group_validator_options(validator_option_list)
        return tuple(cls(**kwargs) for cls, kwargs in options.items())

    @staticmethod
    def _expand_validator_option(validator_class, option, value):
        """Return a suitable option dict based on `option` and `value`."""
        options = {}
        if isinstance(value, dict):
            options = value
        elif (validation.validators.get(option) is None and
                option != validator_class.kind):
            # it's an option name, not the validator kind/alias
            options[option] = value
        elif validator_class.required_options:  # implicit option assignment
            options[validator_class.required_options[0]] = value
        return options

    @classmethod
    def _extract_validator_class_and_options(cls, options):
        """Return a list of valid validator classes with their options."""
        validator_option_list = []
        for option, value in options.items():
            validator_class = cls._get_validator_class_for_option(option)
            should_skip = validator_class is None \
                or cls._should_skip_validator(validator_class, option, value)
            if should_skip:
                continue
            validator_option_list.append((validator_class, option, value))
        return tuple(validator_option_list)

    @staticmethod
    def _get_validator_class_for_option(option):
        """Get validator class by kind or a validation option."""
        try:
            return validation.validators[option]
        except KeyError:
            predicate = lambda cls: option in cls.acceptable_options
            validators = select(validation.validators.values(), predicate)
            if not validators:
                return None
            elif len(validators) > 1:
                template = ("two or more validators are associated with "
                            "'{option}' option")
                raise ArgumentError(template, option=option)
            return validators[0]

    @classmethod
    def _group_validator_options(cls, options):
        """Group the given options by their associated validator class."""
        validator_options = {}
        for validator_class, option, value in options:
            if validator_class not in validator_options:
                validator_options[validator_class] = {}
            update_dict(
                validator_options[validator_class],
                cls._expand_validator_option(validator_class, option, value))
        return validator_options

    @staticmethod
    def _should_skip_validator(cls, option, value):
        # check for value == False only if the validator has no required
        # options, otherwise assume False is the value for the required option
        return option == cls.kind \
            and not cls.required_options \
            and value is False
