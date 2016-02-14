from fatools.core_ext import builtin
from fatools.structutils.interactions import (CompoundStericClashInteraction,
                                              StericClashInteraction)
from fatools.structutils.interactions.finder import (FINDER_REGISTRY,
                                                     InteractionFinder)

builtin.extend_list()


# TODO add docstring
class MultipleInteractionFinder(InteractionFinder):
    def __init__(self, *interactions, **interaction_options):
        self._finders = gather_finders(interactions or ('all',),
                                       interaction_options)

    def _search_interactions(self, st1, as1, st2, as2):
        all_interactions = []
        for finder in self._finders:
            # must pass atom set copies to avoid problems
            interactions = finder._search_interactions(
                st1, list(as1), st2, list(as2))
            all_interactions.extend(interactions)
        return curate_interactions(all_interactions)

    def _sort_interactions(self, interactions):
        return interactions.sorted_by('residues[0]', 'name', 'atom_indexes')


def compact_interactions(interactions):
    """Join together steric-clashes with the same residue."""
    interactions = list(interactions).sorted_by(
        'residues[0]', 'name', 'atom_indexes')
    i = 0
    while i < len(interactions):
        if isinstance(interactions[i], StericClashInteraction):
            j, resnum, sc_list = i, interactions[i].residues[0], []
            while j < len(interactions) and \
                    isinstance(interactions[j], StericClashInteraction) and \
                    interactions[j].residues[0] == resnum:
                sc_list.append(interactions[j])
                j += 1
            if len(sc_list) > 1:
                csc = CompoundStericClashInteraction.from_steric_clashes(
                    sc_list)
                interactions[i:j] = [csc]
        i += 1
    return tuple(interactions)


def curate_interactions(interactions):
    """Select and organize the given list of interactions.

    This includes removing duplicate interactions (i.e., steric clashes),
    joining together interactions into one per residue (only for steric
    clashes) and sorting them.

    """
    interactions = remove_duplicate_interactions(interactions)
    interactions = compact_interactions(interactions)  # already sorted
    return tuple(interactions)


# TODO add docstring
def find_interactions(st1, st2=None, atoms1=None, atoms2=None, **options):
    return MultipleInteractionFinder.find(st1, st2, atoms1, atoms2, **options)


def gather_finders(interactions, interaction_options):
    if len(interactions) == 1 and interactions[0] == 'all':
        return tuple(fcls() for fcls in set(FINDER_REGISTRY.values()))
    finders = [FINDER_REGISTRY[interaction]() for interaction in interactions]
    for interaction, options in interaction_options.items():
        finders.append(FINDER_REGISTRY[interaction](**options))
    return tuple(finders)


def remove_duplicate_interactions(interactions):
    """Remove interaction duplicates.

    An interaction is considered a duplicate when it's a steric-clash and
    the same atoms are forming another interaction.

    """
    # steric-clashes at the end
    sort_key = lambda i: i.name == 'steric-clash'

    interaction_map = dict()
    for interaction in interactions.sorted(sort_key):
        atom_indexes = interaction.atom_indexes.flatten()
        is_duplicate = atom_indexes in interaction_map
        if interaction.name != 'steric-clash' or not is_duplicate:
            interaction_map[atom_indexes] = interaction
    return tuple(interaction_map.values())
