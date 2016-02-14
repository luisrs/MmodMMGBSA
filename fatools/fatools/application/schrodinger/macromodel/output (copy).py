import sys
import csv
sys.path.append('/home/luis/Desktop/FranciscoAdasme/fatools')
from abc import ABCMeta, abstractmethod
from fatools.utils.inflection import underscore
import re
import pprint
import math
from schrodinger import structure


class TextParser():
    __metaclass__ = ABCMeta

    def __init__(self, dtype):
        self.dtype = dtype

    @classmethod
    @abstractmethod
    def construct(self):
        NotImplemented

    @classmethod
    @abstractmethod
    def extract(self):
        NotImplemented

    def after_parsing(self):
        pass

    def before_parsing(self):
        pass

    def parse(self, source):

        if not isinstance(source, file):
            try:
                source = open(source)
            except IOError as e:
                print "I/O error({0}): {1}".format(e.errno, e.strerror)
        self.before_parsing()
        try:
            self.extract(source)
        except StopIteration:
            print "Erorr"
        self.after_parsing()
        obj = self.construct(self.ligands)
        return obj


class Parseable():
    __metaclass__ = ABCMeta

    @classmethod
    @abstractmethod
    def parser(cls):
        pass

    @classmethod
    def from_file(cls, fname):
        return cls.parser().parse(fname)


class EnergyListingResult(Parseable):

    def __init__(self, name, scoring_terms):
        self.name = name
        # print 'EnergyListingResult', name
        # pprint.pprint(scoring_terms)
        # print type(scoring_terms)
        self.intra_energies = scoring_terms['intra_energy']
        self.solvation_energies = scoring_terms['solvation_energy']
        self.probabilities = scoring_terms['probabilities']
        self.total_energies = scoring_terms['total_energy']

    @property
    def intra_unbound(self):
        return sum([intra_e * p_i for intra_e, p_i in zip(
            self.intra_energies, self.probabilities)])

    @property
    def solv_unbound(self):
        return sum([solv_e * p_i for solv_e, p_i in zip(
            self.solvation_energies, self.probabilities)])

    @property
    def entropy(self):
        k_b = 0.008314462
        return -k_b * sum([p_i * math.log(p_i) for p_i in self.probabilities])

    @classmethod
    def parser(cls):
        return EnergyListingParser(cls)


def boltzmann_probabilities(energies, kt=2.479):
    boltzmann_factors = list()
    for ene in energies:
        try:
            boltzmann_factors.append(math.e ** (-ene / kt))
        except OverflowError:
            pass
    partition_function = sum(boltzmann_factors)
    return [bf / partition_function for bf in boltzmann_factors]
    # print "Energies boltzmann_probabilities: ", energies
    # boltzmann_factors = [math.e ** (-ene/kt) for ene in energies]
    # partition_function = sum(boltzmann_factors)
    # return [bf / partition_function for bf in boltzmann_factors]


class EnergyListingParser(TextParser):

    def set(self, name, value):
        setattr(self, name, value)

    def construct(self, ligands):
        return Output(ligands)

    def extract(self, output_file):
        reader = structure.MaestroReader(output_file.name)
        ligand_dict = dict()
        list_ligands = list()
        for st in reader:
            if st.title not in ligand_dict:
                ligand_dict[st.title] = dict()
                ligand_dict[st.title]['total_energy'] = list()
                ligand_dict[st.title]['solvation_energy'] = list()
                ligand_dict[st.title]['intra_energy'] = list()
            ligand_dict[st.title]['total_energy'].append((
                st.property['r_mmod_Potential_Energy-OPLS-2005']))
            ligand_dict[st.title]['solvation_energy'].append((
                st.property['r_mmod_Solvation_Energy-OPLS-2005']))
            ligand_dict[st.title]['intra_energy'].append((
                float(st.property['r_mmod_Potential_Energy-OPLS-2005'])) -
                float(st.property['r_mmod_Solvation_Energy-OPLS-2005']))
        for ligand in ligand_dict:
            ligand_dict[ligand]['probabilities'] = \
                boltzmann_probabilities(
                ligand_dict[ligand]['total_energy'])
            if(ligand_dict[ligand]['probabilities'] is None):
                pass
            else:
                list_ligands.append(EnergyListingResult(
                    ligand, ligand_dict[ligand]))
                self.ligands = tuple(list_ligands)


class InteractionEnergyResult(Parseable):

    def __init__(self, name, atomset1, atomset2, atomset_1_and_2):
        self.set('name', name)
        self.set('atomset1', atomset1)
        self.set('atomset2', atomset2)
        self.set('atomset_1_and_2', atomset_1_and_2)

    def set(self, name, value):
        setattr(self, name, value)

    @property
    def electrostatic(self):
        return self.atomset_1_and_2.electrostatic

    @property
    def vdw(self):
        return self.atomset_1_and_2.van_der_waals

    @property
    def solv_bound(self):
        return ((self.atomset2.solvation_sa) + (self.atomset2.solvation_gb))

    @property
    def intra_bound(self):
        return(self.atomset2.total_energy) - (
            (self.atomset2.solvation_sa) + (self.atomset2.solvation_gb))

    @property
    def strain_protein(self):
        return(self.atomset1.total_energy) - (
            (self.atomset1.solvation_sa) + (self.atomset1.solvation_gb))

    @classmethod
    def parser(cls):
        return InteractionEnergyParser(cls)


class EnergyTerms(object):

    pattern_energies = r' +([a-zA-Z- ]+).+= +(-?\d+\.\d+) \('

    def __init__(self):
        pass

    def parse_energy_listing_energies(self):
        print " parse_energy_listing_energies ola"

    def parse_interaction_energies(self, atomset):
        energy_terms = re.findall(
            self.pattern_energies, atomset)
        for energy_term in energy_terms:
            term = underscore(energy_term[0].strip())
            value = float(energy_term[1])
            setattr(self, term.strip(), value)


class Output(object):

    def __init__(self, ligands):
        self.ligand = dict()
        for ligand in ligands:
            self.ligand[ligand.name] = ligand

    def __getitem__(self, item):
        return self.ligand[item]

    def keys(self):
        return self.ligand.keys()

    def __str__(self):
        return str(self.ligand)

    def __iter__(self):
        return iter(self.ligand)

    def __len__(self):
        return len(self.ligand)


class InteractionEnergyParser(TextParser):

    pattern_title_ligand = (r'.+Read.+\d+ atoms.+\n(.+)')
    atomsets = (r'Atom set   1:|Atom set   2:|Atom sets   1 and   2:')
    format_atomset = (r'({})(.+?)vdW'.format(atomsets))
    pattern_atomset = re.compile(format_atomset, flags=re.DOTALL)

    def set(self, name, value):
        setattr(self, name, value)

    def construct(self, ligands):
        return Output(ligands)

    def merge_ligands_atomsets(self, name_ligand, atom_sets):
        energies = zip(atom_sets[0::3], atom_sets[1::3], atom_sets[2::3])
        dict_ligand_atomsets = dict(zip(name_ligand, energies))
        return dict_ligand_atomsets

    def extract(self, output_file):
        list_ligands = list()
        self.ligands = dict()
        energies_logfile = output_file.read()
        container_atomset = self.pattern_atomset.findall(energies_logfile)
        ligands_titles = re.findall(
            self.pattern_title_ligand, energies_logfile)
        ligands_titles = list(set(ligands_titles))
        ligand_title = [title for title in ligands_titles if 'ligand' in title]
        ligand_atomsets = self.merge_ligands_atomsets(
            ligand_title, container_atomset)
        for ligand, atomsets in ligand_atomsets.iteritems():
            index_atom_set = 0
            self.set('name', ligand.strip())
            for atomset in atomsets:
                n_atomset = atomset[1]
                if(index_atom_set == 0):
                    self.atomset_1 = EnergyTerms()
                    self.atomset_1.parse_interaction_energies(n_atomset)
                elif(index_atom_set == 1):
                    self.atomset_2 = EnergyTerms()
                    self.atomset_2.parse_interaction_energies(n_atomset)
                elif(index_atom_set == 2):
                    self.atomset_1_and_2 = EnergyTerms()
                    self.atomset_1_and_2.parse_interaction_energies(n_atomset)
                index_atom_set += 1
            list_ligands.append(InteractionEnergyResult(
                self.name, self.atomset_1, self.atomset_2,
                self.atomset_1_and_2))
        self.ligands = tuple(list_ligands)



class RRHO_EntropyResult(Parseable):

    def __init__(self, name, TS_trans, TS_rot, TS_vib_, TS_total):
        self.



TdS_trans   TdS_rot TdS_vib TdS_total   Title
-10.7144193485  -9.7247012487   6.3874137105    -14.0517068867  2EXM_minimized_ligand



class RRHO_EntropyParser(TextParser):

    def construc(self, ligands):
        return Output(ligands)

    def extract(self, csv_file):
        row_list = list()
        with open(self.out_cvsfile, 'rb') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
            for row in spamreader:
                row_list.append(row[0].split(','))
        row1 = row_list[0]
        row2 = row_list[1]
        energy_terms = dict(zip(row1, row2))
        return energy_terms


result = RRHO_EntropyResult.from_file('2EXM_entropyRRHO.csv')
# result = EnergyListingResult.from_file('2_complex_energy-out.mae')
# print result['1sqa_ligand'].solv_unbound


# lista_files = ['1sqa.log', '1f8b.log']
# lista_objetos = list()
# for infile in lista_files:
#     result = InteractionEnergyResult.from_file(infile)
#     lista_objetos.append(result)

# for ob in lista_objetos:
#     ligand = ob.keys()[0]
#     print ligand, type(ligand)
# result = InteractionEnergyResult.from_file('1bcu.log')
# print result['1bcu_ligand']
# print result
# ligando = result['1h_p38']
# print ligando.strain_protein
# print "aqui"
# print ligando.vdw

# # output['ligand'] -> InteractionEnergyResult.name
# # for result in output -> InteractionEnergyResult

# result2 = EnergyListingResult.from_file('mmod_energy_listing_aurora-out.mae')
# print result2['2b_AuroraA_ligand'].entropy
