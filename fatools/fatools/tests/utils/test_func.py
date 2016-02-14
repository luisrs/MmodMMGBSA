import unittest
from fatools.utils.kernel import (
    ArgumentError, InvalidArgumentError, MissingArgumentError)
from fatools.utils.func import (
    AttributePredicate, ExclusionPredicate, InclusionPredicate,
    CompoundPredicate, NotFoundError,
    find, flatten, extract, select, transform_values, update_dict)
from fatools.utils.mass_assign import MassAssignable

not_in = ExclusionPredicate
within = InclusionPredicate


class AttributePredicateTests(unittest.TestCase):
    def test_creation_with_keyword_arguments(self):
        predicate = AttributePredicate(attr1=1, attr2='2')

        expected = [('attr1', 1), ('attr2', '2')]
        self.assertEqual(expected, sorted(predicate.items))

    def test_call_with_valid_instance(self):
        instance = MassAssignable(attr1=1, attr2='2')
        predicate = AttributePredicate(attr1=1, attr2='2')
        self.assertTrue(predicate(instance))

    def test_call_with_invalid_instance(self):
        instance = MassAssignable(attr1='abc', attr2='two')
        predicate = AttributePredicate(attr1=1, attr2='2')
        self.assertFalse(predicate(instance))

    def test_call_with_instance_without_attribute(self):
        instance = MassAssignable(attr1=1)
        predicate = AttributePredicate(attr1=1, attr2='2')
        self.assertFalse(predicate(instance))


class CompoundPredicateTests(unittest.TestCase):
    def test_call_with_one_predicate(self):
        predicate = InclusionPredicate(range(3))
        cp = CompoundPredicate(predicate)
        for i in range(-1, 4):
            self.assertEqual(predicate(i), cp(i))

    def test_call_with_two_predicates(self):
        cp = CompoundPredicate(within=range(3), not_in=range(0, 10, 2))
        self.assertTrue(cp(1))

        self.assertFalse(cp(-1))
        self.assertFalse(cp(0))
        self.assertFalse(cp(2))
        self.assertFalse(cp(3))

    def test_call_with_two_predicates_and_any(self):
        cp = CompoundPredicate(within=range(3), not_in=range(0, 10, 2),
                               operator=any)
        self.assertTrue(cp(-1))
        self.assertTrue(cp(0))
        self.assertTrue(cp(1))
        self.assertTrue(cp(2))
        self.assertTrue(cp(3))

        self.assertFalse(cp(4))
        self.assertFalse(cp(6))

    def test_creation_with_one_predicate(self):
        predicate = InclusionPredicate(range(5))
        cp = CompoundPredicate(predicate)
        self.assertEqual(1, len(cp.subpredicates))
        self.assertEqual((predicate,), cp.subpredicates)

    def test_creation_with_named_predicate(self):
        cp = CompoundPredicate(within=range(5))
        self.assertEqual(1, len(cp.subpredicates))
        self.assertIsInstance(cp.subpredicates[0], InclusionPredicate)
        self.assertEqual(range(5), cp.subpredicates[0].items)

    def test_creation_with_predicate_and_named_predicate(self):
        predicate = InclusionPredicate(range(5))
        cp = CompoundPredicate(predicate, not_in=range(3, 10, 2))
        self.assertEqual(2, len(cp.subpredicates))
        self.assertEqual(predicate, cp.subpredicates[0])
        self.assertIsInstance(cp.subpredicates[1], ExclusionPredicate)
        self.assertEqual(range(3, 10, 2), cp.subpredicates[1].items)


class ExclusionPredicateTests(unittest.TestCase):
    def test_call_with_not_included_instance(self):
        predicate = ExclusionPredicate('0123456789')
        self.assertTrue(predicate('a'))

    def test_call_with_included_instance(self):
        predicate = ExclusionPredicate('0123456789')
        self.assertFalse(predicate('0'))

    def test_call_with_invalid_type(self):
        predicate = ExclusionPredicate('0123456789')
        self.assertTrue(predicate(0))


class ExtractTests(unittest.TestCase):
    def setUp(self):
        self.cfg = dict(cpu=8, host='localhost', tpp=2, local=True,
                        njobs=1, debug=False)

    def test_extract_from_invalid_mapping(self):
        with self.assertRaises(InvalidArgumentError) as err:
            extract([], ('cpu',))
        expected_err = "invalid argument 'mapping': []"
        self.assertEqual(expected_err, str(err.exception))

    def test_extract_key(self):
        self.assertEqual(8, extract(self.cfg, 'cpu'))
        self.assertEqual(
            dict(host='localhost', tpp=2, local=True, njobs=1, debug=False),
            self.cfg)

    def test_extract_key_with_default(self):
        self.assertEqual('x.cfg', extract(self.cfg, 'cfg', 'x.cfg'))
        self.assertEqual(
            dict(cpu=8, host='localhost', tpp=2, local=True, njobs=1,
                 debug=False),
            self.cfg)

    def test_extract_keys(self):
        self.assertEqual(
            dict(cpu=8, host='localhost'),
            extract(self.cfg, ('cpu', 'host')))
        self.assertEqual(
            dict(tpp=2, local=True, njobs=1, debug=False),
            self.cfg)

    def test_extract_keys_empty(self):
        self.assertEqual(dict(), extract(self.cfg, []))
        self.assertEqual(
            dict(cpu=8, host='localhost', tpp=2, local=True, njobs=1,
                 debug=False),
            self.cfg)

    def test_extract_keys_with_one_value(self):
        self.assertEqual(
            dict(cpu=8),
            extract(self.cfg, ('cpu',)))
        self.assertEqual(
            dict(host='localhost', tpp=2, local=True, njobs=1, debug=False),
            self.cfg)

    def test_extract_undefined_keys(self):
        self.assertEqual(
            dict(host='localhost'),
            extract(self.cfg, ('procs', 'host')))
        self.assertEqual(
            dict(cpu=8, tpp=2, local=True, njobs=1, debug=False),
            self.cfg)

    def test_extract_with_predicate(self):
        self.assertEqual(
            dict(local=True, debug=False),
            extract(self.cfg, lambda _, v: isinstance(v, bool)))
        self.assertEqual(
            dict(cpu=8, host='localhost', tpp=2, njobs=1),
            self.cfg)

    def test_extract_without_deletion(self):
        self.assertEqual(
            dict(cpu=8, host='localhost'),
            extract(self.cfg, ('cpu', 'host'), delete=False))
        self.assertEqual(
            dict(cpu=8, host='localhost', tpp=2, local=True, njobs=1,
                 debug=False),
            self.cfg)


class InclusionPredicateTests(unittest.TestCase):
    def test_call_with_included_instance(self):
        predicate = InclusionPredicate('0123456789')
        self.assertTrue(predicate('0'))

    def test_call_with_not_included_instance(self):
        predicate = InclusionPredicate('0123456789')
        self.assertFalse(predicate('a'))

    def test_call_with_invalid_type(self):
        predicate = InclusionPredicate('0123456789')
        self.assertFalse(predicate(0))


class FindTests(unittest.TestCase):
    def test_find_with_unknown_predicate(self):
        with self.assertRaises(ArgumentError) as err:
            find('abc', subset='bc')
        self.assertEqual("unknown predicate 'subset'", str(err.exception))

    def test_find_existing_element(self):
        self.assertEqual('a', find('abc', lambda ele: ele == 'a'))

    def test_find_existing_element_with_predicate(self):
        self.assertEqual('a', find('abc', inclusion='a'))

    def test_find_existing_element_with_predicate_alias(self):
        self.assertEqual('a', find('abc', within='ab'))

    def test_find_missing_element(self):
        self.assertEqual(None, find('abc', lambda ele: ele == 'd'))

    def test_find_missing_element_with_custom_default(self):
        self.assertEqual(-1, find('abc', lambda ele: ele == 'd', default=-1))

    def test_find_missing_element_raising_not_found_exception(self):
        with self.assertRaises(NotFoundError) as err:
            find('abc', lambda ele: ele == 'd', silent=False)
        expected_err = 'no element satisfied the given predicates'
        self.assertEqual(expected_err, str(err.exception))


class FlattenTests(unittest.TestCase):
    def test_flatten_dimension_one(self):
        value = list(range(10))
        self.assertEqual(value, flatten(value))

    def test_flatten_dimension_two(self):
        value = [range(5), range(2), range(3)]
        expected = [0, 1, 2, 3, 4, 0, 1, 0, 1, 2]
        self.assertEqual(expected, flatten(value))

    def test_flatten_dimension_mixed(self):
        value = [range(5), 2, range(3), 4]
        expected = [0, 1, 2, 3, 4, 2, 0, 1, 2, 4]
        self.assertEqual(expected, flatten(value))

    def test_skip_string(self):
        value = [range(5), 'two', range(3), 4, 'five']
        expected = [0, 1, 2, 3, 4, 'two', 0, 1, 2, 4, 'five']
        self.assertEqual(expected, flatten(value))


class SelectTests(unittest.TestCase):
    def test_select_with_predicate(self):
        self.assertEqual(('a', 'b'), select('abc', inclusion='ab'))

    def test_select_with_predicate_alias(self):
        self.assertEqual(('c',), select('abc', not_in='ab'))

    def test_select_with_unknown_predicate(self):
        with self.assertRaises(ArgumentError) as err:
            select('abc', subset='bc')
        self.assertEqual("unknown predicate 'subset'", str(err.exception))

    def test_select_without_predicate(self):
        with self.assertRaises(MissingArgumentError) as err:
            select('abc')
        expected_err = 'expected at least one predicate'
        self.assertEqual(expected_err, str(err.exception))

    def test_selecting_multiple_elements(self):
        self.assertEqual(('a', 'b'), select('abc', lambda ele: ele in 'ab'))

    def test_selecting_no_element(self):
        self.assertEqual((), select('abc', lambda ele: ele == 'd'))

    def test_selecting_one_element(self):
        self.assertEqual(('a',), select('abc', lambda ele: ele == 'a'))


class PredicateOperationTests(unittest.TestCase):
    def test_complex_operation(self):
        cp = (within(range(3)) & not_in(range(0, 10, 2))) | within(('a', 1e3))
        self.assertTrue(cp(1))
        self.assertTrue(cp('a'))
        self.assertTrue(cp(1e3))

        self.assertFalse(cp(-1))
        self.assertFalse(cp(0))
        self.assertFalse(cp(2))
        self.assertFalse(cp(3))

    def test_operation_or(self):
        cp = within(range(3)) | not_in(range(0, 10, 2))
        self.assertIsInstance(cp, CompoundPredicate)
        self.assertEqual(2, len(cp.subpredicates))

        self.assertTrue(cp(-1))
        self.assertTrue(cp(0))
        self.assertTrue(cp(1))
        self.assertTrue(cp(2))
        self.assertTrue(cp(3))

        self.assertFalse(cp(4))
        self.assertFalse(cp(6))

    def test_operation_and(self):
        cp = within(range(3)) & not_in(range(0, 10, 2))
        self.assertIsInstance(cp, CompoundPredicate)
        self.assertEqual(2, len(cp.subpredicates))

        self.assertTrue(cp(1))

        self.assertFalse(cp(-1))
        self.assertFalse(cp(0))
        self.assertFalse(cp(2))
        self.assertFalse(cp(3))


class TransformValuesTests(unittest.TestCase):
    def test_transform_values_with_copy(self):
        mapping = dict(local=True, host='anton')
        expected = dict(local='True', host='anton')
        result = transform_values(mapping, str, copy=True)
        self.assertIsNot(result, mapping)
        self.assertDictEqual(expected, result)
        self.assertNotEqual(expected, mapping)

    def test_transform_values_without_copy(self):
        mapping = dict(local=True, host='anton')
        expected = dict(local='True', host='anton')
        result = transform_values(mapping, str)
        self.assertIs(result, mapping)
        self.assertDictEqual(expected, result)
        self.assertDictEqual(expected, mapping)


class UpdateDictTests(unittest.TestCase):
    def setUp(self):
        self.default = dict(cpu=1, host='localhost', debug=False)

    def test_copy_and_update_dict(self):
        arg = dict(local=True, host='anton')
        expected = dict(cpu=1, host='anton', local=True, debug=False)
        result = update_dict(self.default, arg, copy=True)
        self.assertEqual(expected, result)
        self.assertNotEqual(expected, self.default)
        self.assertIsNot(result, self.default)

    def test_update_dict(self):
        expected = dict(cpu=10, host='anton', debug=False)
        self.assertEqual(
            expected,
            update_dict(self.default, dict(cpu=10, host='anton')))
        self.assertEqual(expected, self.default)

    def test_update_dict_with_new_entries(self):
        arg = dict(host='anton', cpu=8, local=False, tpp=4)
        expected = dict(cpu=8, host='anton', local=False, debug=False, tpp=4)
        self.assertEqual(
            expected,
            update_dict(self.default, arg))
        self.assertEqual(expected, self.default)

    def test_update_dict_without_override(self):
        arg = dict(host='anton', cpu=8, local=False, tpp=4)
        expected = dict(cpu=1, host='localhost', local=False, debug=False, tpp=4)
        self.assertEqual(
            expected,
            update_dict(self.default, arg, override=False))
        self.assertEqual(expected, self.default)

if __name__ == '__main__':
    unittest.main()
