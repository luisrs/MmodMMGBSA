import io
import sys
import unittest

from fatools.utils.kernel import (FormattedError, InvalidArgumentError,
                                  InvalidTypeError, KeypathGetter,
                                  MissingArgumentError, ensure_type,
                                  getattrnames, getclassname, getqual,
                                  isiterable, redirect_stream, reraise,
                                  suppress)


class EnsureTypeTests(unittest.TestCase):
    def test_ensure_type_with_multiple_dtype(self):
        val = ('test string',)
        self.assertIs(ensure_type((tuple, list), val), val)

    def test_ensure_type_with_invalid_value(self):
        with self.assertRaises(InvalidTypeError) as err:
            ensure_type(tuple, 'test string')
        expected_err = "invalid value type 'str', expected 'tuple'"
        self.assertEqual(expected_err, str(err.exception))

    def test_ensure_type_with_invalid_value_and_converter(self):
        self.assertEqual(ensure_type(str, 1, converter=str), '1')

    def test_ensure_type_with_invalid_value_and_multiple_dtype(self):
        with self.assertRaises(InvalidTypeError) as err:
            ensure_type((tuple, list), 'test string')
        expected_err = "invalid value type 'str', expected ('tuple', 'list')"
        self.assertEqual(expected_err, str(err.exception))

    def test_ensure_type_with_valid_value(self):
        val = ('test string',)
        self.assertIs(ensure_type(tuple, val), val)

    def test_ensure_type_without_dtype(self):
        val = ['test string']
        self.assertIs(ensure_type(None, val), val)


class FormattedErrorTests(unittest.TestCase):
    def test_creation_of_subclass_without_template(self):
        class SubError(FormattedError):
            __template__ = 'this is a {prefix} template'
        err = SubError(prefix='nice')
        self.assertEqual('this is a nice template', str(err))

    def test_creation_with_simple_string(self):
        err = FormattedError('missing option')
        self.assertEqual('missing option', str(err))

    def test_creation_with_template(self):
        err = FormattedError("missing option '{option}'", option='name')
        self.assertEqual("missing option 'name'", str(err))

    def test_creation_without_arguments(self):
        with self.assertRaises(ValueError) as err:
            FormattedError()
        self.assertEqual('missing required error template', str(err.exception))

    def test_creation_without_template(self):
        with self.assertRaises(ValueError) as err:
            FormattedError(option='name')
        self.assertEqual('missing required error template', str(err.exception))


class GetAttrNamesTests(unittest.TestCase):
    def test_getattrnames(self):
        C = type('C', (), {})
        c = C()
        c.attr1 = 10
        c.attr2 = 'attr2'
        self.assertEqual(('attr1', 'attr2'), getattrnames(c))


class GetClassNameTests(unittest.TestCase):
    def test_getclassname(self):
        self.assertEqual('dict', getclassname(dict))
        self.assertEqual('int', getclassname(int))
        self.assertEqual('C', getclassname(type('C', (), {})))

    def test_getclassname_with_instances(self):
        self.assertEqual('dict', getclassname(dict()))
        self.assertEqual('int', getclassname(10))
        self.assertEqual('C', getclassname(type('C', (), {})()))


class GetQualifierTests(unittest.TestCase):
    def test_qualifier_of_class_with_special_attribute(self):
        C = type('C', (), dict(__qualifier__='custom_qualifier'))
        self.assertEqual('custom_qualifier', getqual(C))

    def test_qualifier_without_prefix_or_suffix(self):
        cls = type('Validator', (), {})
        self.assertEqual('validator', getqual(cls))

    def test_qualifier_with_builtin_class(self):
        self.assertEqual('int', getqual(int))

    def test_qualifier_with_long_suffix(self):
        cls = type('ArgumentValidationError', (), {})
        self.assertEqual('argument', getqual(cls, suffix='ValidationError'))

    def test_qualifier_with_lowercased_prefix(self):
        cls = type('FAPredicate', (), {})
        self.assertEqual('predicate', getqual(cls, prefix='fa'))

    def test_qualifier_with_prefix(self):
        cls = type('FAPredicate', (), {})
        self.assertEqual('predicate', getqual(cls, prefix='FA'))

    def test_qualifier_with_prefix_and_suffix(self):
        cls = type('FAInclusionPredicate', (), {})
        qualifier = getqual(cls, prefix='FA', suffix='Predicate')
        self.assertEqual('inclusion', qualifier)

    def test_qualifier_with_suffix(self):
        cls = type('PresenceValidator', (), {})
        self.assertEqual('presence', getqual(cls, suffix='Validator'))

    def test_qualifier_with_suffix_from_class_with_long_name(self):
        cls = type('MissingArgumentValidationError', (), {})
        qualifier = getqual(cls, suffix='ValidationError')
        self.assertEqual('missing_argument', qualifier)

    def test_qualifier_with_suffix_from_instance(self):
        self.assertEqual('int', getqual(10))

        cls = type('PresenceValidator', (), {})
        self.assertEqual('presence', getqual(cls(), suffix='Validator'))


class InvalidArgumentErrorTests(unittest.TestCase):
    def test_creation(self):
        err = InvalidArgumentError('silent', 1)
        expected_err = "invalid argument 'silent': 1"
        self.assertEqual('silent', err.argname)
        self.assertEqual(1, err.argvalue)
        self.assertEqual(expected_err, str(err))

    def test_creation_with_template(self):
        template = "expected {dtype} for '{name}', got {value} ({value_dtype})"
        err = InvalidArgumentError('silent', 1, template,
                                   dtype='bool', value_dtype='int')
        expected_err = "expected bool for 'silent', got 1 (int)"
        self.assertEqual(expected_err, str(err))


class IterableTests(unittest.TestCase):
    class CustomIterable:
        def __iter__(self):
            return iter(())

    def test_isiterable_empty(self):
        self.assertTrue(isiterable(()))
        self.assertTrue(isiterable([]))
        self.assertTrue(isiterable(''))

    def test_isiterable(self):
        self.assertTrue(isiterable(('a', 'b')))
        self.assertTrue(isiterable(['a', 'b']))
        self.assertTrue(isiterable('ab'))
        self.assertTrue(isiterable(range(10)))
        self.assertTrue(isiterable(i for i in range(10)))

        self.assertFalse(isiterable(5))
        self.assertFalse(isiterable(unittest))

    def test_isiterable_custom_type(self):
        self.assertTrue(isiterable(IterableTests.CustomIterable()))

    def test_isiterable_with_type(self):
        self.assertTrue(isiterable(('a', 'b'), tuple))
        self.assertFalse(isiterable(['a', 'b'], tuple))
        self.assertFalse(isiterable('ab', tuple))
        self.assertFalse(isiterable(range(10), tuple))

        self.assertTrue(isiterable(('a', 'b'), (tuple, list)))
        self.assertTrue(isiterable(['a', 'b'], (tuple, list)))
        self.assertFalse(isiterable('ab', (tuple, list)))
        self.assertFalse(isiterable(xrange(10), (tuple, list)))

    def test_isiterable_of_type(self):
        self.assertTrue(isiterable((), of_type=str))
        self.assertTrue(isiterable(('a', 'b'), of_type=str))
        self.assertFalse(isiterable(('a', 'b', 2, 6), of_type=str))
        self.assertTrue(isiterable(('a', 'b', 2, 6), of_type=(str, int)))


class KeypathGetterTests(unittest.TestCase):
    def test_get_attribute_single(self):
        getter = KeypathGetter('insert')
        value = [1, 2]
        self.assertEqual(value.insert, getter(value))

    def test_get_attribute_multiple(self):
        getter = KeypathGetter('items._len')
        C = type('C', (), {})
        value = C()
        value.items = C()
        value.items._len = 3
        self.assertEqual(3, getter(value))

    def test_get_attribute_multiple_with_index(self):
        getter = KeypathGetter('items[1]._len')
        C = type('C', (), {})
        value = C()
        value.items = [1, C(), 's']
        value.items[1]._len = 3
        self.assertEqual(3, getter(value))

    def test_get_attribute_invalid(self):
        getter = KeypathGetter('items')
        c = type('C', (), {})()
        self.assertRaises(AttributeError, getter, c)

    def test_get_item_single(self):
        getter = KeypathGetter('entries')
        value = dict(entries=[1, dict(count=52, repeat='A'), 's'])
        self.assertIs(value['entries'], getter(value))

    def test_get_item_single_index(self):
        getter = KeypathGetter('1')
        self.assertEqual(2, getter(['one', 2, ['t', 'h', 'r', 'e', 'e']]))

    def test_get_item_multiple_with_index(self):
        getter = KeypathGetter('entries[1].count')
        value = dict(entries=[1, dict(count=52, repeat='A'), 's'])
        self.assertEqual(52, getter(value))

    def test_get_item_multiple_with_index_consecutive(self):
        getter = KeypathGetter('entries[0][2]')
        value = dict(entries=[[4312, 3, 'a'], dict(count=52, repeat='A'), 's'])
        self.assertEqual('a', getter(value))

    def test_get_item_multiple_with_index_consecutive_dotted(self):
        getter = KeypathGetter('entries.0.2')
        value = dict(entries=[[4312, 3, 'a'], dict(count=52, repeat='A'), 's'])
        self.assertEqual('a', getter(value))

    def test_parsing_keypath_multiple(self):
        getter = KeypathGetter('key.key2.key3')
        self.assertEqual(('key', 'key2', 'key3'), getter._items)

    def test_parsing_keypath_multiple_with_index(self):
        getter = KeypathGetter('key.key2[2].key3')
        self.assertEqual(('key', 'key2', 2, 'key3'), getter._items)

    def test_parsing_keypath_multiple_with_index_dotted(self):
        getter = KeypathGetter('key.key2.2.key3')
        self.assertEqual(('key', 'key2', 2, 'key3'), getter._items)

    def test_parsing_keypath_single(self):
        getter = KeypathGetter('key')
        self.assertEqual(('key',), getter._items)

    def test_parsing_keypath_single_with_index(self):
        getter = KeypathGetter('key[1]')
        self.assertEqual(('key', 1), getter._items)

    def test_parsing_keypath_single_with_index_dotted(self):
        getter = KeypathGetter('key.1')
        self.assertEqual(('key', 1), getter._items)

class MissingArgumentErrorTests(unittest.TestCase):
    def test_creation(self):
        err = MissingArgumentError('silent')
        expected_err = "missing required 'silent' argument"
        self.assertEqual('silent', err.argname)
        self.assertEqual(expected_err, str(err))


class RedirectStreamTests(unittest.TestCase):
    def test_redirect_stream(self):
        stream = io.BytesIO()
        self.assertIs(sys.stdout, sys.__stdout__)
        with redirect_stream(stdout=stream):
            self.assertIs(sys.stdout, stream)
            print('test string')
        self.assertIs(sys.stdout, sys.__stdout__)
        self.assertEqual('test string\n', stream.getvalue())


class ReraiseTests(unittest.TestCase):
    def test_reraise(self):
        with self.assertRaisesRegexp(ValueError, 'custom error'):
            try:
                int('a')
            except ValueError as err:
                reraise(err, 'custom error')


class SuppressTests(unittest.TestCase):
    def setUp(self):
        self.data = dict(field='value')

    def test_supress(self):
        with suppress(KeyError):
            self.data['non-existent field']

    def test_supress_multiple_exceptions(self):
        with suppress(KeyError, AttributeError):
            self.data['non-existent field']

        with suppress(KeyError, AttributeError):
            self.data.length


if __name__ == '__main__':
    unittest.main()
