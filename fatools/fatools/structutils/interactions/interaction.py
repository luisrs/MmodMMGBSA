from fatools.application.schrodinger import wrap_atom, wrap_atom_if_needed
from fatools.core_ext import builtin
from fatools.structure import AtomCollection, Ring, is_backbone, is_sidechain
from fatools.utils.caching import cached_property
from fatools.utils.kernel import clsname
from fatools.utils.text import glued
from schrodinger.structutils.measure import (measure_bond_angle,
                                             measure_distance)

builtin.extend_tuple()


# TODO add docstring
class Interaction(object):
    def __init__(self, st1, fragment1, st2, fragment2, **measurements):
        self._structures = (st1, st2)
        self._fragments = (wrap_atom_if_needed(fragment1, st1),
                           wrap_atom_if_needed(fragment2, st2))
        self._measurements = measurements
        self._after_initialize()
        self._calculate_missing_measurements()

    def __getattr__(self, name):
        try:
            return self._measurements[name]
        except KeyError:
            return super(Interaction, self).__getattribute__(name)

    def __str__(self):
        return self.description

    def __repr__(self):
        return '{0}({1[0]}, {1[1]})'.format(clsname(self), self._fragments)

    @cached_property
    def abbreviation(self):
        return interaction_abbreviation(self.name)

    abbr = abbreviation

    @cached_property
    def atom_indexes(self):
        get_idxs = lambda f: getattr(f, 'atom_indexes', (f.index, ))
        return self._fragments.map(get_idxs)

    @cached_property
    def description(self):
        atom_indexes = [str(idxs[0]) if len(idxs) == 1 else
                        '{{{}}}'.format(glued(idxs, ' '))
                        for idxs in self.atom_indexes]
        return '{0}[{1[0]}, {1[1]}]'.format(self.name, atom_indexes)

    @property
    def fragments(self):
        return tuple(self._fragments)

    @property
    def measurement_values(self):
        return tuple(self._measurements[k] for k in self.__measures__)

    @property
    def measurements(self):
        return self._measurements.copy()

    @property
    def name(self):
        return self.__interaction_name__

    @cached_property
    def recep_desc(self):
        return get_interaction_fragment_label(self.fragments[0])

    @cached_property
    def residues(self):
        def get_resnum(f):
            try:
                return f.resnum
            except AttributeError:  # for atom collections
                return f.atom_resnum
        return self._fragments.map(get_resnum).flatten().uniq()

    @property
    def structures(self):
        return tuple(self._structures)

    def _after_initialize(self):
        pass

    def _calculate_missing_measurements(self):
        missing_measures = set(self.__measures__) - set(self._measurements)
        for measure in missing_measures:
            calculator = getattr(self, 'calculate_' + measure)
            self._measurements[measure] = calculator(self._fragments)


class PairwiseInteraction(Interaction):
    __measures__ = ('distance', 'donor_angle', 'acceptor_angle')

    acceptor = property(lambda self: self._sorted_atoms[1])
    atoms = property(lambda self: self.fragments)
    donor = property(lambda self: wrap_atom(self._sorted_atoms[0].bond[1].atom2))

    def calculate_acceptor_angle(self, atoms):
        shared, acc = atoms
        try:
            return measure_bond_angle(acc.bond[1].atom2, acc, shared)
        except IndexError:  # acceptor is a single atom (e.g., water without H)
            return None

    def calculate_distance(self, atoms):
        return measure_distance(*atoms)

    def calculate_donor_angle(self, atoms):
        shared, acc = atoms
        return measure_bond_angle(shared.bond[1].atom2, shared, acc)


def get_interaction_fragment_label(recep_f):
    if isinstance(recep_f, Ring):
        rescode, resnum = recep_f.pdbcode, recep_f.resnum
        f_desc = '{}R'.format(recep_f.size)
    elif isinstance(recep_f, AtomCollection):
        rescode, resnum = recep_f[0].pdbcode, recep_f[0].resnum
        if is_backbone(recep_f):
            f_desc = 'bb'
        elif is_sidechain(recep_f):
            f_desc = 'sc'
        else:
            f_desc = ''
    else:  # it's an atom
        rescode, resnum = recep_f.pdbcode, recep_f.resnum
        f_desc = recep_f.pdbname
    res_desc = '{}{}'.format(rescode, resnum)
    return glued((res_desc, f_desc), ' ').strip()


def interaction_abbreviation(interaction_name):
    return glued(t[0].upper() for t in interaction_name.split('-'))


interaction_abbr = interaction_abbreviation
