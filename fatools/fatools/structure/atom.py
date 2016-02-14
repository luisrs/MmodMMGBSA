# This is just a skeleton for computed properties... no real use for now;
# used by wrapper for _StructureAtom

from fatools.utils.caching import cached_property


# TODO add docstring
class Atom(object):
    def __repr__(self):
        return 'Atom({})'.format(self.name)

    def __str__(self):
        return self.description

    @cached_property
    def description(self):
        return '[{}]:{}:{}{}:({}){}'.format(
            self.index, self.chain, self.pdbres.strip(), self.resnum,
            self.element, self.pdbname.strip())
