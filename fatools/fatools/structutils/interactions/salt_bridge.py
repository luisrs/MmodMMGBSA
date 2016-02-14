from fatools.structutils.interactions import (InteractionCriteria,
                                              register_finder)
from fatools.structutils.interactions.finder import InteractionFinder
from fatools.structutils.interactions.interaction import Interaction
from fatools.utils.enum import Enum
from schrodinger.structutils.interactions.salt_bridge import \
    SaltBridgeFinder as _SaltBridgeFinder
from schrodinger.structutils.measure import measure_distance


class SaltBridgeCriteria(Enum):
    default = InteractionCriteria(max_distance=4)


class SaltBridgeInteraction(Interaction):
    __interaction_name__ = 'salt-bridge'
    __measures__ = ('distance',)

    atoms = property(lambda self: self.fragments)

    def calculate_distance(self, atoms):
        return measure_distance(*atoms)


class SaltBridgeFinder(InteractionFinder):
    __criteria__ = SaltBridgeCriteria
    __interaction__ = SaltBridgeInteraction

    def _search_interactions(self, st1, as1, st2, as2):
        options = dict(
            cutoff=self.criteria.max_distance,
            ignore_same_res=True)
        sb_iter = _SaltBridgeFinder.find(st1, as1, st2, as2, **options)
        return tuple(SaltBridgeInteraction(st1, atom1, st2, atom2)
                     for atom1, atom2 in sb_iter)
register_finder(SaltBridgeFinder)
