from fatools.structutils import get_atoms
from fatools.structutils.interactions import (InteractionCriteria,
                                              register_finder)
from fatools.structutils.interactions.finder import PairwiseInteractionFinder
from fatools.structutils.interactions.interaction import PairwiseInteraction
from fatools.utils.caching import cached_property
from fatools.utils.enum import Enum
from schrodinger.structutils.analyze import evaluate_asl, match_hbond

H_POLAR_ASL = 'atom.ele H and not /C0-H0/'
HBOND_ACCEPTOR_ASL = 'not (atom.ele C H)'
HBOND_ATOMS_ASL = '({}) or ({})'.format(HBOND_ACCEPTOR_ASL, H_POLAR_ASL)


class HydrogenBondCriteria(Enum):
    maestro = InteractionCriteria(
        max_distance=2.8, min_donor_angle=120, min_acceptor_angle=90)
    glide = InteractionCriteria(
        max_distance=2.5, min_donor_angle=90, min_acceptor_angle=60)
    default = maestro
HBondCriteria = HydrogenBondCriteria


class HydrogenBondInteraction(PairwiseInteraction):
    __interaction_name__ = 'h-bond'

    H = hydrogen = property(lambda self: self._sorted_atoms[0])

    @cached_property
    def _sorted_atoms(self):  # ensure H is the first fragment
        atoms = self._fragments
        return tuple(reversed(atoms) if atoms[0].element != 'H' else atoms)
HBondInteraction = HydrogenBondInteraction


class HydrogenBondFinder(PairwiseInteractionFinder):
    __criteria__ = HydrogenBondCriteria
    __interaction__ = HydrogenBondInteraction

    def match(self, atom1, atom2):
        constraints = dict(
            distance_max=self.criteria.max_distance,
            donor_angle=self.criteria.min_donor_angle,
            acceptor_angle=self.criteria.min_acceptor_angle)
        return match_hbond(atom1, atom2, **constraints)

    @staticmethod
    def _setup_atom_sets(st1, as1, st2, as2):
        as1 = frozenset(evaluate_asl(st1, HBOND_ATOMS_ASL)) & frozenset(as1)
        as2 = frozenset(evaluate_asl(st2, HBOND_ATOMS_ASL)) & frozenset(as2)
        return get_atoms(st1, as1), get_atoms(st2, as2)
HBondFinder = HydrogenBondFinder
register_finder(HydrogenBondFinder)
