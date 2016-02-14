from fatools.structure import Atom
from fatools.utils.caching import cached_property
from fatools.utils.kernel import clsname
from schrodinger.structure import _StructureAtom


class AtomWrapper(Atom):
    def __init__(self, atom):
        assert isinstance(atom, _StructureAtom), \
            'invalid atom object: {}'.format(clsname(atom))
        self._schrod_atom = atom

    def __getattr__(self, name):
        return getattr(self._schrod_atom, name)

    @cached_property
    def name(self):
        name = self._schrod_atom.name
        return self.element + str(self.index) if not name else name

    @cached_property
    def pdbname(self):
        pdbname = self._schrod_atom.pdbname.strip()
        return self.name if not pdbname else pdbname
