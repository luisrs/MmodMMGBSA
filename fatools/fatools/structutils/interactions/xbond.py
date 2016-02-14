from fatools.structutils import get_atoms
from fatools.structutils.interactions import (InteractionCriteria,
                                              register_finder)
from fatools.structutils.interactions.finder import PairwiseInteractionFinder
from fatools.structutils.interactions.interaction import PairwiseInteraction
from fatools.utils.caching import cached_property
from fatools.utils.enum import Enum
from schrodinger.structutils.analyze import evaluate_asl

HALOGENS = frozenset(['F', 'Cl', 'Br', 'I'])
HALOGEN_ASL = 'atom.ele F Cl Br I'
XBOND_ACCEPTOR_ASL = 'atom.ele O N'
XBOND_ATOMS_ASL = '({}) or ({})'.format(XBOND_ACCEPTOR_ASL, HALOGEN_ASL)


class HalogenBondCriteria(Enum):
    default = InteractionCriteria(
        max_distance=3.5,
        min_donor_angle=140,
        min_acceptor_angle=90)
    loose = InteractionCriteria(
        max_distance=5,
        min_donor_angle=120,
        min_acceptor_angle=60)


XBondCriteria = HalogenBondCriteria


class HalogenBondInteraction(PairwiseInteraction):
    __interaction_name__ = 'x-bond'

    halogen = X = property(lambda self: self._sorted_atoms[0])

    @cached_property
    def _sorted_atoms(self):  # ensure X is the first fragment
        atoms = self._fragments
        return tuple(reversed(atoms) if not atoms[0].is_halogen else atoms)


XBondInteraction = HalogenBondInteraction


class HalogenBondFinder(PairwiseInteractionFinder):
    __criteria__ = HalogenBondCriteria
    __interaction__ = HalogenBondInteraction

    def __init__(self, criteria=None, exclude_halogens=('F', ), **constraints):
        super(HalogenBondFinder, self).__init__(criteria, **constraints)
        self.excluded_halogens = exclude_halogens

    def match(self, atom1, atom2):
        constraints = dict(
            max_distance=self.criteria.max_distance,
            donor_angle=self.criteria.min_donor_angle,
            acceptor_angle=self.criteria.min_acceptor_angle,
            exclude_halogens=self.excluded_halogens)
        return match_xbond(atom1, atom2, **constraints)

    @staticmethod
    def _setup_atom_sets(st1, as1, st2, as2):
        as1 = frozenset(evaluate_asl(st1, XBOND_ATOMS_ASL)) & frozenset(as1)
        as2 = frozenset(evaluate_asl(st2, XBOND_ATOMS_ASL)) & frozenset(as2)
        return get_atoms(st1, as1), get_atoms(st2, as2)


XBondFinder = HalogenBondFinder
register_finder(HalogenBondFinder)


def match_xbond(atom1, atom2,
                max_distance=3.5,
                donor_angle=140,
                acceptor_angle=90,
                exclude_halogens=('F', ),
                return_values=False):
    halogen, acceptor = (atom1, atom2) if atom1.is_halogen else (atom2, atom1)
    if halogen.element not in HALOGENS - set(exclude_halogens or ()):
        return False

    interaction = HalogenBondInteraction(None, halogen, None, acceptor)
    criteria = InteractionCriteria(
        max_distance=max_distance,
        min_donor_angle=donor_angle,
        min_acceptor_angle=acceptor_angle)
    match_xbond = criteria.match_interaction(interaction)
    if return_values:
        return (match_xbond, ) + interaction.measurement_values
    return match_xbond
