from fatools.structure import Atom
from fatools.utils.caching import cached_property
from fatools.utils.collection import Collection
from fatools.utils.inflection import singularize
from fatools.utils.kernel import clsname
from fatools.utils.text import glued


# TODO add docstring
class AtomCollection(Collection):
    def __init__(self, st, atoms):
        super(AtomCollection, self).__init__(atoms, dtype=Atom)
        self._st = st
    structure = st = property(lambda self: self._st)

    def __getattr__(self, name):
        if name.startswith('atom_'):  # fetch atoms' attribute
            return self.fetch_all(singularize(name[5:]))
        return super(AtomCollection, self).__getattribute__(name)

    def __repr__(self):
        return '{}({})'.format(clsname(self), glued(self.atom_names, ' '))

    @cached_property
    def description(self):
        return '[{}-{}]:{{{}}}'.format(
            self[0].index, self[-1].index,
            glued(map(str.strip, self.atom_pdbnames), ' '))
