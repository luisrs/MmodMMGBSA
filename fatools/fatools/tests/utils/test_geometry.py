import unittest

import numpy as np
from fatools.utils.geometry import (Plane, measure_angle,
                                    measure_dihedral_angle, measure_distance,
                                    measure_plane_angle)


class MeasureAngleTests(unittest.TestCase):
    def test_measure_angle_with_vectors(self):
        angle = measure_angle([3, 4], [-8, 6])
        self.assertEqual(90, angle)

    def test_measure_angle_with_points(self):
        angle = measure_angle(
            [-0.871019, -3.915519, 2.403598],
            [0.075125, -2.098154, 1.929842],
            [1.311066, 0.561562, 1.328446])
        self.assertAlmostEqual(177.102806566, angle, 9)

        angle = measure_angle(
            [-1.072402, -3.222503, 3.313817],
            [-0.109673, -1.804572, 2.493067],
            [1.311066, 0.561562, 1.328446])
        self.assertAlmostEqual(176.022718008, angle, 9)


class MeasureDistanceTests(unittest.TestCase):
    def test_measure_distance(self):
        distance = measure_distance(
            [0.075125, -2.098154, 1.929842],
            [1.311066, 0.561562, 1.328446])
        self.assertAlmostEqual(2.99387984144, distance, 11)


class MeasurePlaneAngleTests(unittest.TestCase):
    def test_measure_plane_angle(self):
        angle = measure_plane_angle(Plane(2, -1, 1, -1), Plane(1, 0, 1, 3))
        self.assertAlmostEqual(30, angle)

        angle = measure_plane_angle(Plane(1, 2, -1, 1), Plane(1, -1, 3, 4))
        self.assertAlmostEqual(119.49620849656642, angle, 14)

    def test_measure_plane_angle_with_points(self):
        points = [
            [-0.86692, 1.404998, 0.770964],
            [0.610095, 1.520094, 1.071593],
            [1.311066, 0.561562, 1.328446],
            [0.075125, -2.098154, 1.929842]]
        angle = measure_plane_angle(points[:3], points[1:])
        self.assertAlmostEqual(12.2552319891, angle, 10)

        points = [
            [-0.798867, 1.676027, 1.596674],
            [0.610095, 1.520094, 1.071593],
            [1.311066, 0.561562, 1.328446],
            [0.075125, -2.098154, 1.929842]]
        angle = measure_plane_angle(points[:3], points[1:])
        self.assertAlmostEqual(27.9947482263, angle, 10)


class MeasureDihedralAngleTests(unittest.TestCase):
    def test_measure_dihedral_angle_with_points(self, ):
        points = [
            [-0.86692, 1.404998, 0.770964],
            [0.610095, 1.520094, 1.071593],
            [1.311066, 0.561562, 1.328446],
            [0.075125, -2.098154, 1.929842]]
        angle = measure_dihedral_angle(*points)
        self.assertAlmostEqual(-12.2552319891, angle, 10)

        points = [
            [-0.798867, 1.676027, 1.596674],
            [0.610095, 1.520094, 1.071593],
            [1.311066, 0.561562, 1.328446],
            [0.075125, -2.098154, 1.929842]]
        angle = measure_dihedral_angle(*points)
        self.assertAlmostEqual(27.9947482263, angle, 10)

    def test_measure_dihedral_angle_with_vectors(self):
        a = np.array([-0.86692, 1.404998, 0.770964])
        b = np.array([0.610095, 1.520094, 1.071593])
        c = np.array([1.311066, 0.561562, 1.328446])
        d = np.array([0.075125, -2.098154, 1.929842])
        ab, bc, cd = b - a, c - b, d - c
        angle = measure_dihedral_angle(ab, bc, cd)
        self.assertAlmostEqual(-12.2552319891, angle, 10)


class PlaneTests(unittest.TestCase):
    def test_creation_with_coefficients(self):
        plane = Plane(-30, 48, -17, -15)
        self.assertEqual((-30, 48, -17, -15), plane.coef)

    def test_creation_with_points(self):
        plane = Plane([1, 2, 3], [4, 6, 9], [12, 11, 9])
        self.assertEqual((-30, 48, -17, -15), plane.coef)


if __name__ == '__main__':
    unittest.main()
