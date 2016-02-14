from collections import Iterable
from numbers import Number

import numpy as np
from fatools.utils.multipledispatch import dispatch


# TODO add docstring
class Plane(object):
    """ax + by + cz + d = 0"""
    @dispatch(Number, Number, Number, Number)
    def __init__(self, a, b, c, d):  # coefficieints
        self.coef = (a, b, c, d)

    @dispatch(Iterable, Iterable, Iterable)
    def __init__(self, a, b, c):
        self.__init__(*Plane.calculate_plane_equation(a, b, c))
    normal = property(lambda self: self.coef[:3])

    @staticmethod
    def calculate_plane_equation(a, b, c):
        a, b, c = map(np.array, (a, b, c))
        ab, ac = b - a, c - a
        cp = np.cross(ab, ac)
        return tuple(cp) + (-np.dot(cp, a),)


# TODO add docstring
@dispatch(Iterable, Iterable)
def measure_angle(v1, v2):
    normal_norm = np.linalg.norm(np.cross(v1, v2))
    return np.degrees(np.arctan2(normal_norm, np.dot(v1, v2)))


# TODO add docstring
@dispatch(Iterable, Iterable, Iterable)
def measure_angle(a, b, c):
    a, b, c = map(np.array, (a, b, c))
    return measure_angle(a - b, c - b)


# TODO add docstring
def measure_distance(a, b):
    return np.linalg.norm(np.array(a) - np.array(b))


# TODO add docstring
@dispatch(Iterable, Iterable, Iterable)
def measure_dihedral_angle(v1, v2, v3):
    n1, n2 = np.cross(v1, v2), np.cross(v2, v3)
    return np.degrees(np.arctan2(
        np.dot(np.cross(n1, n2), v2 / np.linalg.norm(v2)),
        np.dot(n1, n2)))


# TODO add docstring
@dispatch(Iterable, Iterable, Iterable, Iterable)
def measure_dihedral_angle(a, b, c, d):
    a, b, c, d = map(np.array, (a, b, c, d))
    return measure_dihedral_angle(b - a, c - b, d - c)


# TODO add docstring
@dispatch(Plane, Plane)
def measure_plane_angle(plane1, plane2):
    return measure_angle(plane1.normal, plane2.normal)


# TODO add docstring
@dispatch(Iterable, Iterable)
def measure_plane_angle(a, b):
    return measure_plane_angle(Plane(*a), Plane(*b))
