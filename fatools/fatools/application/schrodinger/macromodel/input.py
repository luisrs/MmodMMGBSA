import os
from subprocess import call

from fatools.utils.func import update_dict
from fatools.utils.schemable import FieldInfo, Schema
from fatools.application.schrodinger.macromodel import (
    ChargesFrom, Cutoff, ElectrostaticTreatment, ForceField, Jobtype, Solvent,
    ConfSearchMethod, ConfSearchTorsionSampling,
    EmbraceComplexConvergeOn, EmbraceComplexMiniMethod, EmbraceMode,
    EnergyReportOption)


# TODO add docstring
class MacromodelInput(Schema):
    jobtype = FieldInfo(inclusion=(Jobtype.available_options()))
    force_field = FieldInfo(
        default=ForceField.opls2005, converter=ForceField,
        inclusion=ForceField.available_options())
    solvent = FieldInfo(
        default=Solvent.gbsa, converter=Solvent,
        inclusion=Solvent.available_options())
    dielectric_constant = FieldInfo(default=1, inclusion=(-1, 1, 2))
    electrostatic_treatment = FieldInfo(
        default=ElectrostaticTreatment.constant_dielectric,
        converter=ElectrostaticTreatment,
        inclusion=ElectrostaticTreatment.available_options())
    charges_from = FieldInfo(
        default=ChargesFrom.force_field,
        inclusion=ChargesFrom.available_options())
    cutoff = FieldInfo(
        default=Cutoff.extended, inclusion=Cutoff.available_options())
    use_substructure_file = FieldInfo(default=True, dtype=bool)

    def write(self, in_file=None, maefile=None, outfile=None):
        if in_file is None and maefile is not None:
            in_file = os.path.splitext(maefile)[0] + '.in'
        elif in_file is None and maefile is None:
            raise ValueError('.mae file is required')

        if isinstance(in_file, str):
            in_file = open(in_file, 'w')
            should_close_after_write = True
        else:
            should_close_after_write = False
        if outfile:
            in_file.write(
                'INPUT_STRUCTURE_FILE {}\nOUTPUT_STRUCTURE_FILE {}\n'.format(
                    maefile, outfile))
        else:
            in_file.write('INPUT_STRUCTURE_FILE {}\n'.format(maefile))
        for field in self._fields:
            in_file.write('{keyword} {value}\n'.format(
                keyword=field.upper(),
                value=getattr(self, field)))
        if should_close_after_write:
            in_file.close()


class ConfSearchInput(MacromodelInput):
    confsearch_method = FieldInfo(
        default=ConfSearchMethod.mcmm,
        inclusion=ConfSearchMethod.available_options())
    inconfs_per_search = FieldInfo(default=0, greater_than_or_equal_to=0)
    outconfs_per_search = FieldInfo(default=100, greater_than_or_equal_to=1)
    confsearch_steps = FieldInfo(default=1000, greater_than_or_equal_to=1)
    confsearch_steps_per_rotatable = FieldInfo(default=50,
                                               greater_than_or_equal_to=1)
    confsearch_torsion_sampling = FieldInfo(
        default=ConfSearchTorsionSampling.extended,
        inclusion=ConfSearchTorsionSampling.available_options())
    energy_window = FieldInfo(default=21.0, greater_than_or_equal_to=1)
    retain_mirror_image = FieldInfo(default=True, dtype=bool)
    conformer_elimination_method = FieldInfo(default='RMSD')
    conformer_elimination_value = FieldInfo(default=0.5,
                                            greater_than_or_equal_to=0)

    def __init__(self, **kwargs):
        update_dict(kwargs, dict(jobtype=Jobtype.ConfSearch))
        super(ConfSearchInput, self).__init__(**kwargs)


class EmbraceMinimizationInput(MacromodelInput):
    complex_mini_method = FieldInfo(
        default=EmbraceComplexMiniMethod.prcg,
        inclusion=EmbraceComplexMiniMethod.available_options())
    complex_maximum_iteration = FieldInfo(
        default=1000, greater_than_or_equal_to=1)
    complex_converge_on = FieldInfo(
        default=EmbraceComplexConvergeOn.gradient,
        inclusion=EmbraceComplexConvergeOn.available_options())
    complex_convergence_threshold = FieldInfo(default=0.05)
    mode = FieldInfo(
        default=EmbraceMode.interaction_energy,
        inclusion=EmbraceMode.available_options())

    def __init__(self, **kwargs):
        update_dict(kwargs, dict(jobtype=Jobtype.Mbaemini))
        super(EmbraceMinimizationInput, self).__init__(**kwargs)


class EnergyInput(MacromodelInput):
    energy_report_option = FieldInfo(
        default=EnergyReportOption.fullreport,
        inclusion=EnergyReportOption.available_options())

    def __init__(self, **kwargs):
        update_dict(kwargs, dict(jobtype=Jobtype.Energy))
        super(EnergyInput, self).__init__(**kwargs)


class RRHOEntropy:

    def __init__(self, infile, out_cvsfile=None, radius=None):
        if(out_cvsfile is None):
            self.out_cvsfile = os.path.splitext(infile)[0] + '_entropyRRHO.csv'
        self.command = "$SCHRODINGER/run rrho_entropy.py {} -csv {}".format(
            infile, self.out_cvsfile)
        if(radius is not None):
            r = " -r {}".format(str(radius))
            self.command = self.command + r

    def run(self):
        call(self.command, shell=True)

# ifile = EnergyInput(use_substructure_file=False)
# ifile.write(in_file='input.in', maefile='1SQA.mae', outfile='salida.mae')

# ifile = ConfSearchInput(use_substructure_file=False)
# print ifile.__dict__
# ifile.write(maefile='1SQA.mae')
