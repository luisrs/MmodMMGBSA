from fatools.application.schrodinger.structure.atom import AtomWrapper
from fatools.structure import Atom, AtomCollection


def wrap_atom(atom):
    return AtomWrapper(atom)


def wrap_atom_if_needed(atom, st=None):
    if isinstance(atom, (AtomWrapper, Atom, AtomCollection)):
        return atom
    if isinstance(atom, int):
        if st is None:
            raise ValueError('cannot wrap atom index: missing structure')
        atom = st.atom[atom]
    return wrap_atom(atom)
