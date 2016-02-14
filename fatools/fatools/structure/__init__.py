from fatools.structure.atom import Atom
from fatools.structure.atom_collection import AtomCollection
from fatools.structure.ring import Ring

BACKBONE_ATOM_PDBNAMES = {'C', 'O', 'N', 'H', 'CA', 'HA'}
PROTEIN_RESIDUES = {
    'ALA', 'ARG', 'ASN', 'ASP', 'CYS', 'GLN', 'GLU', 'GLY', 'HIS', 'HIP',
    'HIE', 'ILE', 'LEU', 'LYS', 'MET', 'PHE', 'PRO', 'SER', 'THR', 'TRP',
    'TYR', 'VAL', 'HID', 'ACE', 'NMA'
}


def is_backbone(atoms):
    return is_protein(atoms) and \
        all(atom.pdbname.strip() in BACKBONE_ATOM_PDBNAMES for atom in atoms)


def is_protein(atoms):
    return all(atom.pdbres.strip() in PROTEIN_RESIDUES for atom in atoms)


def is_sidechain(atoms):
    return is_protein(atoms) and \
        all(atom.pdbname.strip() not in BACKBONE_ATOM_PDBNAMES
            for atom in atoms)
