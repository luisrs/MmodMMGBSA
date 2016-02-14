from fatools.structure import Ring
from fatools.structutils import get_atoms
from fatools.structutils.interactions import (InteractionCriteria,
                                              register_finder)
from fatools.structutils.interactions.finder import InteractionFinder
from fatools.structutils.interactions.interaction import Interaction
from fatools.utils.enum import Enum
from schrodinger.structutils.interactions import (find_pi_cation_interactions,
                                                  find_pi_pi_interactions)


class CationPiCriteria(Enum):
    default = InteractionCriteria(
        max_distance=30)


class PiPiCriteria(Enum):
    default = InteractionCriteria(
        max_face_to_face_distance=30,
        max_edge_to_face_distance=60)


class CationPiInteraction(Interaction):
    __interaction_name__ = 'cation-pi'
    __measures__ = ('distance', 'angle')

    cation = property(lambda self: self._fragments[0])
    ring = property(lambda self: self._fragments[1])


class PiPiInteraction(Interaction):
    __interaction_name__ = 'pi-pi'
    __measures__ = ('distance', 'angle', 'face_to_face')

    rings = property(lambda self: self.fragments)


class CationPiFinder(InteractionFinder):
    __criteria__ = CationPiCriteria
    __interaction__ = CationPiInteraction

    def _search_interactions(self, st1, as1, st2, as2):
        sst1, sst2 = st1.extract(as1), st2.extract(as2)
        sst1._st_id, sst2._st_id = 1, 2
        c_pi_interactions = find_pi_cation_interactions(sst1, sst2)
        c_pi_interactions = [c_pi for c_pi in c_pi_interactions
                             if self.criteria.match_measurements(
                                 distance=c_pi.distance)]
        return tuple(CationPiFinder._map_interaction(c_pi, st1, as1, st2, as2)
                     for c_pi in c_pi_interactions)

    @staticmethod
    def _map_interaction(c_pi, st1, as1, st2, as2):
        if c_pi.cation_structure._st_id == 2:
            st1, st2 = st2, st1
            as1, as2 = as2, as1
        as1 = get_atoms(st1, [as1[i - 1] for i in c_pi.cation_centroid.atoms])
        as2 = get_atoms(st2, [as2[i - 1] for i in c_pi.pi_centroid.atoms])
        ring = Ring(st2, as2, c_pi.pi_centroid.xyz)
        measurements = dict(distance=c_pi.distance, angle=c_pi.angle)
        return CationPiInteraction(st1, as1[0], st2, ring, **measurements)
register_finder(CationPiFinder)


class PiPiFinder(InteractionFinder):
    __criteria__ = PiPiCriteria
    __interaction__ = PiPiInteraction

    def _search_interactions(self, st1, as1, st2, as2):
        sst1, sst2 = st1.extract(as1), st2.extract(as2)
        constraints = dict(
            max_ftf_dist=self.criteria.max_face_to_face_distance,
            max_etf_dist=self.criteria.max_edge_to_face_distance)
        pi_pi_interactions = find_pi_pi_interactions(sst1, sst2, **constraints)
        return tuple(PiPiFinder._map_interaction(pi_pi, st1, as1, st2, as2)
                     for pi_pi in pi_pi_interactions)

    @staticmethod
    def _map_interaction(pi_pi, st1, as1, st2, as2):
        as1 = get_atoms(st1, [as1[idx - 1] for idx in pi_pi.ring1.atoms])
        as2 = get_atoms(st2, [as2[idx - 1] for idx in pi_pi.ring2.atoms])
        ring1 = Ring(st1, as1, pi_pi.ring1.xyz)
        ring2 = Ring(st2, as2, pi_pi.ring2.xyz)
        return PiPiInteraction(
            st1, ring1,
            st2, ring2,
            distance=pi_pi.distance,
            angle=pi_pi.angle,
            face_to_face=pi_pi.face_to_face)
register_finder(PiPiFinder)
