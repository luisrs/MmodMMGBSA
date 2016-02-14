import unittest
from fatools.utils.mass_assign import MassAssignable, MassAssignmentError


class MassAssignmentTests(unittest.TestCase):
    class Loose(MassAssignable):
        pass

    class Restricted(MassAssignable):
        assignable_attributes = ('one', 'two')
        guarded_attributes = ('three',)

    def test_loose_state(self):
        L = MassAssignmentTests.Loose
        self.assertTrue(L.can_assign_attribute('one'))
        self.assertTrue(L.can_assign_attribute('two'))
        self.assertTrue(L.can_assign_attribute('three'))
        self.assertTrue(L.can_assign_attribute('four'))

        self.assertFalse(L.is_attribute_guarded('one'))
        self.assertFalse(L.is_attribute_guarded('two'))
        self.assertFalse(L.is_attribute_guarded('three'))
        self.assertFalse(L.is_attribute_guarded('four'))

    def test_restricted_state(self):
        R = MassAssignmentTests.Restricted
        self.assertTrue(R.can_assign_attribute('one'))
        self.assertTrue(R.can_assign_attribute('two'))
        self.assertFalse(R.can_assign_attribute('three'))
        self.assertFalse(R.can_assign_attribute('four'))

        self.assertFalse(R.is_attribute_guarded('one'))
        self.assertFalse(R.is_attribute_guarded('two'))
        self.assertTrue(R.is_attribute_guarded('three'))
        self.assertFalse(R.is_attribute_guarded('four'))

    def test_mass_assign(self):
        data = dict(one=1, two=2, three=3, four=4)
        obj = MassAssignmentTests.Loose(**data)
        for attr in data.keys():
            self.assertEqual(data[attr], getattr(obj, attr))
        self.assertEqual('Loose(four=4, one=1, three=3, two=2)', repr(obj))

    def test_mass_assign_guarded_attributes(self):
        with self.assertRaises(MassAssignmentError):
            MassAssignmentTests.Restricted(one=1, three=3)

    def test_mass_assign_non_assignable_attributes(self):
        obj = MassAssignmentTests.Restricted(one=1, two=2, four=4)
        for i, attr in enumerate(['one', 'two']):
            self.assertEqual(i + 1, getattr(obj, attr))
        self.assertRaises(AttributeError, getattr, obj, 'four')
        self.assertEqual('Restricted(one=1, two=2)', repr(obj))

if __name__ == '__main__':
    unittest.main()
