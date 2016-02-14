from fatools.core_ext import builtin
from fatools.structure import AtomCollection
from fatools.structutils.interactions import (InteractionCriteria,
                                              register_finder)
from fatools.structutils.interactions.finder import InteractionFinder
from fatools.structutils.interactions.interaction import (
    Interaction, get_interaction_fragment_label)
from fatools.utils.caching import cached_property
from fatools.utils.enum import Enum
from fatools.utils.statistics import mean
from schrodinger.structutils.interactions.steric_clash import clash_iterator
from schrodinger.structutils.measure import measure_distance

builtin.extend_list()
builtin.extend_tuple()


class StericClashCriteria(Enum):
    default = InteractionCriteria(min_overlap=0.4)


class StericClashInteraction(Interaction):
    __interaction_name__ = 'steric-clash'
    __measures__ = ('distance', 'overlap')

    atoms = property(lambda self: self.fragments)

    @cached_property
    def recep_desc(self):
        recep_f = AtomCollection(self._structures[0], [self._fragments[0]])
        return get_interaction_fragment_label(recep_f)

    @cached_property
    def relative_overlap(self):
        return self.overlap / self.vdw_radii_sum

    @cached_property
    def vdw_radii_sum(self):
        return self.atoms[0].vdw_radius + self.atoms[1].vdw_radius

    def calculate_distance(self, atoms):
        return measure_distance(*atoms)

    def calculate_overlap(self, atoms):
        return self.vdw_radii_sum - self.distance


class CompoundStericClashInteraction(Interaction):
    __interaction_name__ = 'steric-clash'
    __measures__ = ('distance', 'overlap')

    @cached_property
    def relative_overlap(self):
        return self.overlap / self.vdw_radii_sum

    @cached_property
    def vdw_radii_sum(self):
        return mean(self._calculate_all_vdw_radii_sums())

    @classmethod
    def from_steric_clashes(cls, steric_clashes):
        atoms = list.with_capacity(2)
        for i in range(2):
            atoms[i] = steric_clashes.pluck('atoms[{}]'.format(i))
            if len(atoms[i].pluck('resnum').uniq()) != 1:
                raise ValueError('atoms belong to different residues')
        st1, st2 = steric_clashes[0].structures
        return cls(st1, AtomCollection(st1, atoms[0]),
                   st2, AtomCollection(st2, atoms[1]))

    def calculate_distance(self, fragments):
        return mean(self._calculate_all_distances())

    def calculate_overlap(self, atoms):
        return self.vdw_radii_sum - self.distance

    def _calculate_all_distances(self):
        return tuple([measure_distance(a1, a2)
                      for a1, a2 in zip(*self._fragments)])

    def _calculate_all_vdw_radii_sums(self):
        return tuple([a1.vdw_radius + a2.vdw_radius
                      for a1, a2 in zip(*self._fragments)])


class StericClashFinder(InteractionFinder):
    __criteria__ = StericClashCriteria
    __interaction__ = StericClashInteraction

    def _search_interactions(self, st1, as1, st2, as2):
        options = dict(allowable_overlap=self.criteria.min_overlap)
        sc_iter = clash_iterator(st1, as1, st2, as2, **options)
        return tuple(StericClashInteraction(st1, atom1, st2, atom2, distance=d)
                     for atom1, atom2, d in sc_iter)
register_finder(StericClashFinder)
