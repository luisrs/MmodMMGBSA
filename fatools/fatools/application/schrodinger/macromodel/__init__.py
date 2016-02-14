from fatools.utils.enum import Enum


class MacromodelOptions(Enum):
    @classmethod
    def available_options(cls):
        return tuple(cls)

    def __str__(self):
        return str(self.value)


class ChargesFrom(MacromodelOptions):
    force_field = 'Force field'
    structure_file = 'Structure file'


class Cutoff(MacromodelOptions):
    extended = 'Extended'
    normal = 'Normal'
    none = 'None'


class ElectrostaticTreatment(MacromodelOptions):
    constant_dielectric = 'Constant dielectric'
    distance_dependent = 'Distance-dependent'
    force_field_defined = 'Force field defined'


class ForceField(MacromodelOptions):
    mm2 = 'MM2*'
    mm3 = 'MM3*'
    amber = 'AMBER'
    opls = 'OPLS'
    mmff = 'MMFF'
    mmffs = 'MMFFs'
    opls2001 = 'OPLS_2001'
    opls2005 = 'OPLS_2005'


class Jobtype(MacromodelOptions):
    ConfSearch = 'CONFSEARCH'
    Mbaemini = 'EMBRACE_MINIMIZATION'
    Energy = 'ENERGY_LISTING'


class Solvent(MacromodelOptions):
    water = 'Water'
    octanol = 'Octanol'
    chcl3 = 'CHCL3'
    gbsa = 'GB/SA'
    none = 'None'


class ConfSearchOptions(MacromodelOptions):
    pass


class ConfSearchMethod(ConfSearchOptions):
    mcmm = 'MCMM'
    confgen = 'Confgen'
    lowmode = 'Lowmode'
    mixed = 'Mixed'
    cgen = 'cgen'
    lmod = 'lmod'
    lmcs = 'lmcs'


class ConfSearchTorsionSampling(ConfSearchOptions):
    restricted = 'Restricted'
    intermediate = 'Intermediate'
    enhanced = 'Enhanced'
    extended = 'Extended'


class EmbraceOptions(MacromodelOptions):
    pass


class EmbraceComplexConvergeOn(EmbraceOptions):
    gradient = 'Gradient'
    energy = 'Energy'
    movement = 'Movement'
    nothing = 'Nothing'


class EmbraceComplexMiniMethod(EmbraceOptions):
    prcg = 'PRCG'
    tncg = 'TNCG'
    osvm = 'OSVM'
    sd = 'SD'
    fmnr = 'FMN'
    lbfgs = 'LBFGS'
    optimal = 'Optimal'


class EmbraceMode(EmbraceOptions):
    energy_difference = 'EnergyDifference'
    interaction_energy = 'InteractionEnergy'


class EnergyOptions(MacromodelOptions):
    pass


class EnergyReportOption(EnergyOptions):
    logfile = 'LOGFILE'
    mmofile = 'MMOFILE'
    fullreport = 'FULLREPORT'
