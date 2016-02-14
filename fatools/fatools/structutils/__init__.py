from fatools.application.schrodinger import wrap_atom
from fatools.structure import Atom
from schrodinger.structutils.analyze import find_ligands, evaluate_asl


# TODO add docstring
def atom_description(self):
    return '[{}]:{}:{}{}:({}){}'.format(
        self.index, self.chain, self.pdbres.strip(), self.resnum, self.element,
        self.pdbname.strip())


# TODO add docstring
def get_atoms(st, atom_idxs):
    wrap_if_needed = lambda a: a if isinstance(a, Atom) else wrap_atom(a)
    return tuple(wrap_if_needed(st.atom[i]) for i in atom_idxs)


# TODO add docstring
def get_ligand_atom_idxs(st):
    ligands = find_ligands(st)
    if not ligands:
        return None
    elif len(ligands) > 1:
        raise ValueError('multiple ligands are not supported')
    return ligands[0].atom_indexes


# TODO add docstring
def parse_atom_set(st, atom_set, default=None):
    if atom_set is None and default is not None:
        atom_set = default
    if isinstance(atom_set, str):
        if atom_set == 'ligand':
            return get_ligand_atom_idxs(st)
        atom_set = evaluate_asl(st, atom_set)
    return atom_set if atom_set else None
