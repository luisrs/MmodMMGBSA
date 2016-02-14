import abc
from itertools import product

from fatools.core_ext import builtin
from fatools.structutils import parse_atom_set
from fatools.utils.kernel import getqualifier

builtin.extend_list()

FINDER_REGISTRY = dict()


# TODO add docstring
class InteractionFinder(object):
    def __init__(self, criteria=None, **constraints):
        self.criteria = self.__class__._setup_criteria(criteria, constraints)

    @classmethod
    def find(cls, st1, st2=None, atoms1=None, atoms2=None, **options):
        return cls(**options).search(st1, st2, atoms1, atoms2)

    def search(self, st1, st2=None, atoms1=None, atoms2=None):
        st2 = st2 if st2 is not None else st1
        as1 = parse_atom_set(st1, atoms1, default='all')
        as2 = parse_atom_set(st2, atoms2, default='all')

        if not as1 or not as2:
            raise ValueError('atom sets cannot be empty')
        interactions = self._search_interactions(st1, as1, st2, as2)
        return self._sort_interactions(interactions).freeze()

    @abc.abstractmethod
    def _search_interactions(self, st1, as1, st2, as2):
        return NotImplemented

    @classmethod
    def _setup_criteria(cls, criteria, constraints):
        if isinstance(criteria, cls.__criteria__):
            return criteria.replace(**constraints)
        elif isinstance(criteria, str):
            return cls.__criteria__[criteria].value
        elif constraints:
            return cls.__criteria__(**constraints)
        # all criteria enums must have a default
        return cls.__criteria__['default'].value

    def _sort_interactions(self, interactions):
        return interactions.sorted_by('residues[0]', 'atom_indexes')


# TODO add docstring
class PairwiseInteractionFinder(InteractionFinder):
    @abc.abstractmethod
    def match(self, *args, **kwargs):
        return NotImplemented

    def _search_interactions(self, st1, as1, st2, as2):
        as1, as2 = self._setup_atom_sets(st1, as1, st2, as2)
        return [self.__interaction__(st1, atom1, st2, atom2)
                for atom1, atom2 in product(as1, as2)
                if self.match(atom1, atom2)]

    @abc.abstractmethod
    def _setup_atom_sets(st1, as1, st2, as2):
        return NotImplemented


def register_finder(finder):
    key = getqualifier(finder, suffix='Finder')
    FINDER_REGISTRY[key.replace('_', '-')] = finder
    FINDER_REGISTRY[finder.__interaction__.__interaction_name__] = finder
