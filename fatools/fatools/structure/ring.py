from fatools.structure import AtomCollection
from fatools.utils.caching import cached_property
from fatools.utils.text import glued


class Ring(AtomCollection):
    def __init__(self, st, atoms, centroid=None):
        super(Ring, self).__init__(st, atoms)
        self._centroid = tuple(centroid)
    centroid = property(lambda self: self._centroid)
    chain = property(lambda self: self[0].chain)
    pdbcode = property(lambda self: self[0].pdbcode.strip())
    pdbres = property(lambda self: self[0].pdbres.strip())
    resnum = property(lambda self: self[0].resnum)
    size = property(lambda self: len(self))

    def __str__(self):
        return self.description

    @cached_property
    def description(self):
        return '[{}-{}]:{}:{}{}:{{{}}}'.format(
            self[0].index, self[-1].index, self.chain, self.pdbres,
            self.resnum, glued(map(str.strip, self.atom_pdbnames), ' '))
