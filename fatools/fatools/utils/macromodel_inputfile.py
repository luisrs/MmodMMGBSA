from abc import abstractmethod
from fatools.utils.schemable import FieldInfo, Schema
from enum import Enum
import os


class InputFile(Schema):

    @abstractmethod
    def write(self, infile):
        pass


class MacromodelInputFile(InputFile):

    def write(self, infile=None, maefile=None):
        if infile is None and maefile is not None:
            infile = os.path.splitext(maefile)[0] + '.in'
        elif infile is None and maefile is None:
            raise ValueError('.mae file is required')

        keywords = ''
        for field in self._fields:
            keywords = keywords + str(field).upper() + ' ' + str(getattr(self, field)) + '\n'
        simpl_file = open(infile, "w")
        simpl_file.write('INPUT_STRUCTURE_FILE ' + maefile)
        simpl_file.write('\n')
        simpl_file.write(keywords)
        simpl_file.close()

    force_field = FieldInfo(default='OPLS_2005', inclusion=('MM2*', 'MM3*', 'AMBER*', 'AMBER94', 'OPLS', 'MMFF', 'MMFFs', 'OPLS_2001', 'OPLS_2005'))
    solvent = FieldInfo(default='GB/SA', inclusion=('None', 'Water', 'Octanol', 'CHCL3', 'GB/SA'))
    dielectric_constant = FieldInfo(default=1, inclusion=(-1, 1, 2))
    electrostatic_treatment = FieldInfo(default='Constant dielectric', inclusion=('Constant dielectric', 'Distance-dependent', 'Force field defined'))
    charges_from = FieldInfo(default='Force field', inclusion=('Force field', 'Structure file'))
    cutoff = FieldInfo(default='Extended', inclusion=('Normal', 'Extended', 'None'))
    use_substructure_file = FieldInfo(default=True, inclusion=(True, False))


class ForceField(Enum):
    MM2 = 'MM2*'
    MM3 = 'MM3*'
    AMBER = 'AMBER'
    OPLS = 'OPLS'
    MMFF = 'MMFF'
    MMFFS = 'MMFFs'
    OPLS2001 = 'OPLS_2001'
    OPLS2015 = 'OPLS_2015'


class Solvent(Enum):
    WATER = 'Water'
    OCTANOL = 'Octanol'
    CHCL3 = 'CHCL3'
    GBSA = 'GB/SA'
    NONE = 'None'


class ElectrostaticTreatment(Enum):
    CONSTANT_DIELECTRIC = 'Constante dielectric'
    DISTANCE_DEPENDENT = 'Distance-dependent'
    FORCE_FIELD_DEFINED = 'Force field defined'


class ChargesFrom(Enum):
    FORCE_FIELD = 'Force field'
    STRUCTURE_FILE = 'Structure file'


class Cutoff(Enum):
    EXTENDED = 'Extended'
    NORMAL = 'Normal'
    NONE = 'None'


class EnergyListing(MacromodelInputFile):

    jobtype = FieldInfo(default='ENERGY_LISTING')
    energy_report_option = FieldInfo(default='FULLREPORT', inclusion=('LOGFILE', 'MMOFILE', 'FULLREPORT'))


class EnergyReportOption(Enum):
    LOGFILE = 'LOGFILE'
    MMOFILE = 'MMOFILE'
    FULLREPORT = 'FULLREPORT'


class ConformationalSearch(MacromodelInputFile):

    jobtype = FieldInfo(default='CONFSEARCH')
    confsearch_method = FieldInfo(default='MCMM', inclusion=('MCMM', 'Confgen', 'Lowmode', 'Mixed', 'cgen', 'lmod', 'lmcs'))
    inconfs_per_search = FieldInfo(default=0, greater_than_or_equal_to=0)
    outconfs_per_search = FieldInfo(default=100, greater_than_or_equal_to=1)
    confsearch_steps = FieldInfo(default=1000, greater_than_or_equal_to=1)
    confsearch_steps_per_rotatable = FieldInfo(default=50, greater_than_or_equal_to=1)
    confsearch_torsion_sampling = FieldInfo(default='Extended', inclusion=('Restricted', 'Intermediate', 'Enhanced', 'Extended'))
    energy_window = FieldInfo(default=21.0, greater_than_or_equal_to=1)
    retain_mirror_image = FieldInfo(default=True, inclusion=(True, False))
    conformer_elimination_method = FieldInfo(default='RMSD')
    conformer_elimination_value = FieldInfo(default=0.5, greater_than_or_equal_to=0)


class ConfsearchMethod(Enum):
    MCMM = 'MCMM'
    CONFGEN = 'Confgen'
    LOWMODE = 'Lowmode'
    MIXED = 'Mixed'
    CGEN = 'cgen'
    LMOD = 'lmod'
    LMCS = 'lmcs'


class EmbraceMinimization(MacromodelInputFile):

    jobtype = FieldInfo(default='EMBRACE_MINIMIZATION')
    complex_mini_method = FieldInfo(default='PRCG', inclusion=('PRCG', 'TNCG', 'OSVM', 'SD', 'FMNR', 'LBFGS', 'Optimal'))
    complex_maximum_iteration = FieldInfo(default=1000)
    complex_converge_on = FieldInfo(default='Gradient', inclusion=('Gradient', 'Energy', 'Movement', 'Nothing'))
    complex_convergence_threshold = FieldInfo(default=0.05)
    mode = FieldInfo(default='InteractionEnergy', inclusion=('EnergyDifference', 'InteractionEnergy'))


class MmodMMGBSA():

    # ifile = EmbraceMinimization(mode=EmbraceMinimization.INTERACTION_MODE)
    # ifile.mode = EmbraceMinimization.INTERACTION_MODE
    # ifile = EmbraceMinimization(mode = MinimizationMode.difference)
    print(type(ForceField.MM2))
    ifile = EmbraceMinimization(force_field=ForceField.MM2)
    ifile.write(maefile='1AQ1_pv.mae')
