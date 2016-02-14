import unittest

from fatools.application.schrodinger.macromodel.input import (
    EmbraceMinimizationInput)

from fatools.application.schrodinger.macromodel import (
    ChargesFrom, ComplexConvergeOn, ComplexMiniMethod, ConfSearchMethod,
    ConfSearchTorsionSampling, Cutoff, ElectrostaticTreatment,
    EnergyReportOption, ForceField, Jobtype, Mode, Solvent)


class EnumParametersTest(unittest.TestCase):

    def test_macromodel_enum_parameters(self):

        self.assertEqual(str(ForceField.opls2005), 'OPLS_2005')
        self.assertEqual(str(Solvent.gbsa), 'GB/SA')
        self.assertEqual(str(
            ElectrostaticTreatment.constant_dielectric),
            'Constant dielectric')
        self.assertEqual(str(ChargesFrom.force_field), 'Force field')
        self.assertEqual(str(Cutoff.extended), 'Extended')

    def test_mabemini_enum_parameters(self):
        ifile = EmbraceMinimizationInput()
        self.assertEqual(ifile.complex_convergence_threshold, 0.05)
        self.assertEqual(str(ComplexMiniMethod.prcg), 'PRCG')
        self.assertEqual(str(ComplexConvergeOn.gradient,), 'Gradient')
        self.assertEqual(str(ComplexConvergeOn.gradient,), 'Gradient')
        self.assertEqual(str(Mode.interaction_energy), 'InteractionEnergy')

    def test_confsearch_enum_parameters(self):
        self.assertEqual(str(ConfSearchMethod.mcmm), 'MCMM')
        self.assertEqual(str(ConfSearchTorsionSampling.extended), 'Extended')
