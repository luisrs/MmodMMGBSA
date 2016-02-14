import unittest

from fatools.structutils.interactions import InteractionCriteria
from fatools.utils.kernel import InvalidArgumentError, MissingArgumentError


class InteractionCriteriaTests(unittest.TestCase):
    def setUp(self):
        self.criteria = InteractionCriteria(
            max_distance=3.5, min_distance=2, min_donor_angle=140,
            acceptor_angle=(120, 170))

    def test_access_as_mapping(self):
        self.assertEqual((2, 3.5), self.criteria['distance'])
        self.assertEqual(140, self.criteria['min_donor_angle'])
        self.assertEqual(170, self.criteria['max_acceptor_angle'])

    def test_access_by_measure(self):
        self.assertEqual((2, 3.5), self.criteria.distance)
        self.assertEqual((140, None), self.criteria.donor_angle)
        self.assertEqual((120, 170), self.criteria.acceptor_angle)

    def test_access_by_measure_with_prefix(self):
        self.assertEqual(2, self.criteria.min_distance)
        self.assertEqual(3.5, self.criteria.max_distance)

        self.assertEqual(140, self.criteria.min_donor_angle)
        self.assertEqual(None, self.criteria.max_donor_angle)

        self.assertEqual(120, self.criteria.min_acceptor_angle)
        self.assertEqual(170, self.criteria.max_acceptor_angle)

    def test_access_measures(self):
        expected = dict(
            distance=(2, 3.5),
            donor_angle=(140, None),
            acceptor_angle=(120, 170))
        self.assertIsNot(self.criteria.measures, self.criteria._measures)
        self.assertDictEqual(expected, self.criteria.measures)

    def test_initialization_with_invalid_argument(self):
        with self.assertRaises(InvalidArgumentError):
            InteractionCriteria(distance=3.5)

    def test_match_constraints(self):
        self.assertTrue(self.criteria.match_measurements(
            distance=2.4, donor_angle=156, acceptor_angle=159))
        self.assertFalse(self.criteria.match_measurements(
            distance=2.4, donor_angle=129, acceptor_angle=159))

    def test_match_constraints_with_missing_measure(self):
        with self.assertRaises(MissingArgumentError) as err:
            self.criteria.match_measurements(distance=2.4, acceptor_angle=159)
        expected = 'missing required \'donor_angle\' measurement'
        self.assertEqual(expected, str(err.exception))

    def test_match_constraints_with_optional_measure(self):
        self.assertTrue(self.criteria.match_measurements(
            distance=2.4, donor_angle=156, acceptor_angle=None))

    def test_replace(self):
        criteria = self.criteria.replace(min_distance=None)
        expected = dict(
            distance=(None, 3.5),
            donor_angle=(140, None),
            acceptor_angle=(120, 170))
        self.assertIsNot(criteria, self.criteria)
        self.assertDictEqual(expected, criteria.measures)

if __name__ == '__main__':
    unittest.main()
