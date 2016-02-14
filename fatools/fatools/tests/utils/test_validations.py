import unittest
from collections import Mapping
from fatools.utils.kernel import ArgumentError
from fatools.utils.validation import (
    validators as validator_registry,
    ExclusionValidator, FormatValidator, InclusionValidator, PresenceValidator,
    NumericalityValidator, PredicateValidator, TypeValidator,
    ValidationOptionParser,
    OptionValidationError, ValidationError)


class ValidationTests(unittest.TestCase):
    def test_validator_registry(self):
        self.assertIsInstance(validator_registry, Mapping)
        self.assertIs(validator_registry['numericality'],
                      NumericalityValidator)
        self.assertIs(validator_registry['within'],
                      InclusionValidator)


class ExclusionValidatorTests(unittest.TestCase):
    def test_kind(self):
        self.assertEqual('exclusion', ExclusionValidator.kind)

    def test_acceptable_options(self):
        expected = ('allow_none', 'choices')
        self.assertEqual(expected, ExclusionValidator.acceptable_options)

    def test_exclusion(self):
        validator = ExclusionValidator(choices=[1, 2, 3])
        self.assertTrue(validator('name', 5))
        self.assertTrue(validator('name', '1'))

    def test_exclusion_invalid(self):
        validator = ExclusionValidator(choices=[1, 2, 3])
        with self.assertRaises(ValidationError) as err:
            self.assertFalse(validator('name', 1))
        expected_err = "value for 'name' must not be one of [1, 2, 3], got 1"
        self.assertEqual(expected_err, str(err.exception))


class FormatValidatorTests(unittest.TestCase):
    def test_kind(self):
        self.assertEqual('format', FormatValidator.kind)

    def test_acceptable_options(self):
        expected = ('allow_none', 'pattern')
        self.assertEqual(expected, FormatValidator.acceptable_options)

    def test_validate_format(self):
        validator = FormatValidator(pattern=r'^Validation\smacros \w+!$')
        self.assertTrue(validator('name', 'Validation macros rule!'))

        with self.assertRaises(ValidationError) as err:
            validator('name', "i'm incorrect")
        expected_err = "'name' does not match expected format"
        self.assertEqual(expected_err, str(err.exception))

    def test_validate_format_numeric(self):
        validator = FormatValidator(pattern=r'^[1-9][0-9]*$')
        self.assertTrue(validator('name', '1'))

        for invalid_str in ('72x', '-11', '03', 'z44', '5v7'):
            self.assertFalse(validator('name', invalid_str, silent=True))

    def test_validate_format_of_non_string(self):
        validator = FormatValidator(pattern=r'^[1-9][0-9]*$')
        with self.assertRaises(ValidationError) as err:
            validator('name', 1)
        expected_err = "'name' is not a string"
        self.assertEqual(expected_err, str(err.exception))

    def test_validate_format_without_pattern(self):
        with self.assertRaises(OptionValidationError) as err:
            FormatValidator()
        expected_err = "format validator: missing required 'pattern' option"
        self.assertEqual(expected_err, str(err.exception))


class InclusionValidatorTests(unittest.TestCase):
    def test_kind(self):
        self.assertEqual('inclusion', InclusionValidator.kind)

    def test_acceptable_options(self):
        expected = ('allow_none', 'choices')
        self.assertEqual(expected, InclusionValidator.acceptable_options)

    def test_inclusion(self):
        validator = InclusionValidator(choices=[1, 2, 3])
        self.assertTrue(validator('name', 1))
        self.assertTrue(validator('name', 2))
        self.assertTrue(validator('name', 3))

    def test_inclusion_invalid(self):
        validator = InclusionValidator(choices=[1, 2, 3])
        with self.assertRaises(ValidationError) as err:
            self.assertFalse(validator('name', 4))
        expected_err = "value for 'name' must be one of [1, 2, 3], got 4"
        self.assertEqual(expected_err, str(err.exception))


class NumericalityValidatorTests(unittest.TestCase):
    def test_kind(self):
        self.assertEqual('numericality', NumericalityValidator.kind)

    def test_acceptable_options(self):
        expected = (
            'allow_none', 'eq', 'equal_to', 'even', 'ge', 'greater_than',
            'greater_than_or_equal_to', 'gt', 'le', 'less_than',
            'less_than_or_equal_to', 'lt', 'ne', 'odd', 'only_integer',
            'other_than')
        self.assertEqual(expected, NumericalityValidator.acceptable_options)

    def test_equal_to(self):
        validator = NumericalityValidator(equal_to=1.23)
        self.assertTrue(validator('name', 1.23))

        with self.assertRaises(ValidationError) as err:
            validator('name', 1.22)
        expected_err = "'name' is not equal to 1.23"
        self.assertEqual(expected_err, str(err.exception))

    def test_even(self):
        validator = NumericalityValidator(even=True)
        self.assertTrue(validator('name', 2))

        with self.assertRaises(ValidationError) as err:
            validator('name', 1)
        expected_err = "'name' is not even"
        self.assertEqual(expected_err, str(err.exception))

    def test_false_option(self):
        validator = NumericalityValidator(odd=False)
        self.assertNotIn('odd', validator.options)

    def test_greater_than(self):
        validator = NumericalityValidator(greater_than=0)
        self.assertTrue(validator('name', 5))

        with self.assertRaises(ValidationError) as err:
            validator('name', -1)
        expected_err = "'name' is less than or equal to 0"
        self.assertEqual(expected_err, str(err.exception))

    def test_greater_than_or_equal_to(self):
        validator = NumericalityValidator(greater_than_or_equal_to=0)
        self.assertTrue(validator('name', 0))

        with self.assertRaises(ValidationError) as err:
            validator('name', -1)
        expected_err = "'name' is less than 0"
        self.assertEqual(expected_err, str(err.exception))

    def test_less_than(self):
        validator = NumericalityValidator(less_than=0)
        self.assertTrue(validator('name', -5))

        with self.assertRaises(ValidationError) as err:
            validator('name', 1)
        expected_err = "'name' is greater than or equal to 0"
        self.assertEqual(expected_err, str(err.exception))

    def test_less_than_or_equal_to(self):
        validator = NumericalityValidator(less_than_or_equal_to=0)
        self.assertTrue(validator('name', 0))

        with self.assertRaises(ValidationError) as err:
            validator('name', 1)
        expected_err = "'name' is greater than 0"
        self.assertEqual(expected_err, str(err.exception))

    def test_odd(self):
        validator = NumericalityValidator(odd=True)
        self.assertTrue(validator('name', 1))

        with self.assertRaises(ValidationError) as err:
            validator('name', 2)
        expected_err = "'name' is not odd"
        self.assertEqual(expected_err, str(err.exception))

    def test_other_than(self):
        validator = NumericalityValidator(other_than=1.23)
        self.assertTrue(validator('name', 1.22))

        with self.assertRaises(ValidationError) as err:
            validator('name', 1.23)
        expected_err = "'name' is equal to 1.23"
        self.assertEqual(expected_err, str(err.exception))

    def test_invalid_option(self):
        with self.assertRaises(OptionValidationError) as err:
            NumericalityValidator(greater_than='5')
        expected_err = ("numericality validator: 'greater_than' option must "
                        "be a number")
        self.assertEqual(expected_err, str(err.exception))

    def test_multiple_options(self):
        validator = NumericalityValidator(greater_than=8, even=True)
        self.assertTrue(validator('name', 10))

        with self.assertRaises(ValidationError) as err:
            validator('name', 8)
        expected_err = "'name' is less than or equal to 8"
        self.assertEqual(expected_err, str(err.exception))

        with self.assertRaises(ValidationError) as err:
            validator('name', 9)
        expected_err = "'name' is not even"
        self.assertEqual(expected_err, str(err.exception))

    def test_numericality_of_int(self):
        self.assertTrue(NumericalityValidator()('name', 5))

    def test_numericality_of_float(self):
        self.assertTrue(NumericalityValidator()('name', 5.7))

    def test_numericality_of_non_number(self):
        with self.assertRaises(ValidationError) as err:
            self.assertTrue(NumericalityValidator()('name', '5.7'))
        expected_err = "'name' is not a number"
        self.assertEqual(expected_err, str(err.exception))

    def test_only_integer(self):
        validator = NumericalityValidator(only_integer=True)
        self.assertTrue(validator('name', 5))

    def test_only_integer_with_float(self):
        validator = NumericalityValidator(only_integer=True)
        with self.assertRaises(ValidationError) as err:
            self.assertFalse(validator('name', 5.))
        expected_err = "'name' is not an integer"
        self.assertEqual(expected_err, str(err.exception))

    def test_short_name(self):
        validator = NumericalityValidator(gt=8)
        self.assertIn('greater_than', validator.options)
        self.assertNotIn('gt', validator.options)


class ValidationOptionParserTests(unittest.TestCase):
    def test_parse_explicit_options(self):
        options = dict(
            numericality={'greater_than': 0},
            type={'dtype': int},
            exclusion={'choices': (10, 20)})
        validators = ValidationOptionParser.parse(options)
        self.assertEqual(3, len(validators))

        validators = dict((v.kind, v) for v in validators)
        for cls in (ExclusionValidator, NumericalityValidator, TypeValidator):
            self.assertIsInstance(validators[cls.kind], cls)

        self.assertEqual({'greater_than': 0, 'allow_none': False},
                         validators['numericality'].options)
        self.assertEqual({'dtype': (int,), 'allow_none': False},
                         validators['type'].options)
        self.assertEqual({'choices': (10, 20), 'allow_none': False},
                         validators['exclusion'].options)

    def test_parse_implicit_options(self):
        options = dict(
            type=int,
            inclusion=(10, 20))
        validators = ValidationOptionParser.parse(options)
        self.assertEqual(2, len(validators))

        validators = dict((v.kind, v) for v in validators)
        for cls in (InclusionValidator, TypeValidator):
            self.assertIsInstance(validators[cls.kind], cls)

        self.assertEqual({'dtype': (int,), 'allow_none': False},
                         validators['type'].options)
        self.assertEqual({'choices': (10, 20), 'allow_none': False},
                         validators['inclusion'].options)

    def test_parse_non_unique_options(self):
        options = dict(choices=('a', 'b'))
        with self.assertRaises(ArgumentError) as err:
            ValidationOptionParser.parse(options)
        self.assertEqual(
            "two or more validators are associated with 'choices' option",
            str(err.exception))

    def test_parse_option_alias(self):
        options = dict(within=(10, 20))
        validators = ValidationOptionParser.parse(options)
        self.assertEqual(1, len(validators))
        self.assertIsInstance(validators[0], InclusionValidator)
        self.assertEqual({'choices': (10, 20), 'allow_none': False},
                         validators[0].options)

    def test_parse_options_without_explicit_validator_names(self):
        options = dict(
            pattern=r'pattern',
            greater_than=88)
        validators = ValidationOptionParser.parse(options)
        self.assertEqual(2, len(validators))

        validators = dict((v.kind, v) for v in validators)
        for cls in (FormatValidator, NumericalityValidator):
            self.assertIsInstance(validators[cls.kind], cls)

        self.assertEqual({'pattern': r'pattern', 'allow_none': False},
                         validators['format'].options)
        self.assertEqual({'greater_than': 88, 'allow_none': False},
                         validators['numericality'].options)

    def test_parse_options_with_flags(self):
        options = dict(presence=True, numericality=True)
        validators = ValidationOptionParser.parse(options)
        self.assertEqual(2, len(validators))

        validators = dict((v.kind, v) for v in validators)
        for cls in (PresenceValidator, NumericalityValidator):
            self.assertIsInstance(validators[cls.kind], cls)

        self.assertEqual({'allow_none': False},
                         validators['presence'].options)
        self.assertEqual({'allow_none': False},
                         validators['numericality'].options)

    def test_parse_options_with_negative_flags(self):
        options = dict(numericality=False)
        validators = ValidationOptionParser.parse(options)
        self.assertEqual(0, len(validators))

    def test_parse_unknown_options(self):
        options = dict(numericality=True, attr1='attr1', attr2='attr2')
        validators = ValidationOptionParser.parse(options)
        self.assertEqual(1, len(validators))
        self.assertIsInstance(validators[0], NumericalityValidator)

        self.assertEqual(
            dict(numericality=True, attr1='attr1', attr2='attr2'), options)


class PredicateValidatorTests(unittest.TestCase):
    def test_validate_predicate(self):
        validator = PredicateValidator(predicate=lambda obj: obj < 10)
        self.assertTrue(validator('name', 5))

    def test_validate_predicate_invalid(self):
        validator = PredicateValidator(predicate=lambda obj: obj < 10)
        with self.assertRaises(ValidationError) as err:
            validator('name', 25)

        expected_err = "invalid value for field 'name', got 25"
        self.assertEqual(expected_err, str(err.exception))

    def test_validate_predicate_with_non_callable(self):
        with self.assertRaises(OptionValidationError) as err:
            PredicateValidator(predicate=10)
        expected_err = "predicate validator: expected a callable object"
        self.assertEqual(expected_err, str(err.exception))


class PresenceValidatorTests(unittest.TestCase):
    def test_kind(self):
        self.assertEqual('presence', PresenceValidator.kind)

    def test_acceptable_options(self):
        expected = ('allow_none',)
        self.assertEqual(expected, PresenceValidator.acceptable_options)

    def test_presence(self):
        self.assertTrue(PresenceValidator()('name', 'Francisco'))

    def test_presence_missing(self):
        with self.assertRaisesRegexp(ValidationError, 'missing') as err:
            PresenceValidator()('name', None)
        self.assertEqual("'name' is missing", str(err.exception))


class TypeValidatorTests(unittest.TestCase):
    def test_kind(self):
        self.assertEqual('type', TypeValidator.kind)

    def test_acceptable_options(self):
        expected = ('allow_none', 'dtype')
        self.assertEqual(expected, TypeValidator.acceptable_options)

    def test_creation_validator_without_dtype(self):
        with self.assertRaises(OptionValidationError) as err:
            TypeValidator()
        expected_err = "type validator: missing required 'dtype' option"
        self.assertEqual(expected_err, str(err.exception))

    def test_creation_validator_with_invalid_dtype(self):
        with self.assertRaises(OptionValidationError) as err:
            TypeValidator(dtype='str')
        expected_err = ("type validator: expected a tuple of classes, "
                        "got ('str',)")
        self.assertEqual(expected_err, str(err.exception))

    def test_type_checking(self):
        validator = TypeValidator(dtype=int)
        self.assertTrue(validator('count', 23))

    def test_type_checking_multiple(self):
        validator = TypeValidator(dtype=(int, str))
        self.assertTrue(validator('count', 23))
        self.assertTrue(validator('count', '23'))

    def test_type_checking_invalid(self):
        validator = TypeValidator(dtype=str)
        with self.assertRaises(ValidationError) as err:
            validator('count', 23)
        expected_msg = ("invalid value for 'count', expected str type, "
                        "got 23 (int)")
        self.assertEqual(expected_msg, str(err.exception))

    def test_type_checking_invalid_multiple(self):
        validator = TypeValidator(dtype=(str, list))
        with self.assertRaises(ValidationError) as err:
            validator('count', 23)
        expected_msg = ("invalid value for 'count', "
                        "expected str or list type, "
                        "got 23 (int)")
        self.assertEqual(expected_msg, str(err.exception))

if __name__ == '__main__':
    unittest.main()
