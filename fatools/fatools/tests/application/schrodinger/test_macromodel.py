import io
import textwrap
import unittest

from fatools.application.schrodinger.macromodel.input import (
    ConfSearchInput, EmbraceMinimizationInput, EnergyInput)

from fatools.application.schrodinger.macromodel import (
    ForceField, ConfSearchMethod, ConfSearchTorsionSampling, EmbraceMode,
    EnergyReportOption)


class InputParametersTest(unittest.TestCase):
    def test_mbaemini_default_parameters(self):
        expected = textwrap.dedent("""\
            INPUT_STRUCTURE_FILE 1AQ1_pv.mae
            CUTOFF Extended
            FORCE_FIELD OPLS_2005
            SOLVENT GB/SA
            COMPLEX_MINI_METHOD PRCG
            USE_SUBSTRUCTURE_FILE True
            JOBTYPE EMBRACE_MINIMIZATION
            COMPLEX_CONVERGENCE_THRESHOLD 0.05
            ELECTROSTATIC_TREATMENT Constant dielectric
            MODE InteractionEnergy
            DIELECTRIC_CONSTANT 1
            CHARGES_FROM Force field
            COMPLEX_CONVERGE_ON Gradient
            COMPLEX_MAXIMUM_ITERATION 1000
            """)

        with io.BytesIO() as stream:
            ifile = EmbraceMinimizationInput()
            ifile.write(stream, maefile='1AQ1_pv.mae')

            self.assertMultiLineEqual(expected, stream.getvalue())

    def test_mbaemini_assigned_parameters(self):
        expected = textwrap.dedent("""\
            INPUT_STRUCTURE_FILE 1AQ1_pv.mae
            CUTOFF Extended
            FORCE_FIELD OPLS_2001
            SOLVENT GB/SA
            COMPLEX_MINI_METHOD PRCG
            USE_SUBSTRUCTURE_FILE True
            JOBTYPE EMBRACE_MINIMIZATION
            COMPLEX_CONVERGENCE_THRESHOLD 0.05
            ELECTROSTATIC_TREATMENT Constant dielectric
            MODE EnergyDifference
            DIELECTRIC_CONSTANT 1
            CHARGES_FROM Force field
            COMPLEX_CONVERGE_ON Gradient
            COMPLEX_MAXIMUM_ITERATION 1000
            """)

        with io.BytesIO() as stream:
            ifile = EmbraceMinimizationInput(
                force_field=ForceField.opls2001,
                mode=EmbraceMode.energy_difference)
            ifile.write(stream, maefile='1AQ1_pv.mae')

            self.assertMultiLineEqual(expected, stream.getvalue())

    def test_confsearch__default_parameters(self):
        expected = textwrap.dedent("""\
            INPUT_STRUCTURE_FILE 1AQ1_pv.mae
            CUTOFF Extended
            OUTCONFS_PER_SEARCH 100
            SOLVENT GB/SA
            CONFORMER_ELIMINATION_METHOD RMSD
            CONFSEARCH_STEPS 1000
            INCONFS_PER_SEARCH 0
            CONFSEARCH_TORSION_SAMPLING Extended
            CONFSEARCH_METHOD MCMM
            CONFORMER_ELIMINATION_VALUE 0.5
            FORCE_FIELD OPLS_2005
            ELECTROSTATIC_TREATMENT Constant dielectric
            JOBTYPE CONFSEARCH
            ENERGY_WINDOW 21.0
            DIELECTRIC_CONSTANT 1
            CHARGES_FROM Force field
            USE_SUBSTRUCTURE_FILE True
            CONFSEARCH_STEPS_PER_ROTATABLE 50
            RETAIN_MIRROR_IMAGE True
            """)

        with io.BytesIO() as stream:
            ifile = ConfSearchInput()
            ifile.write(stream, maefile='1AQ1_pv.mae')

            self.assertMultiLineEqual(expected, stream.getvalue())

    def test_confsearch_assigned_parameters(self):
        expected = textwrap.dedent("""\
            INPUT_STRUCTURE_FILE 1AQ1_pv.mae
            CUTOFF Extended
            OUTCONFS_PER_SEARCH 100
            SOLVENT GB/SA
            CONFORMER_ELIMINATION_METHOD RMSD
            CONFSEARCH_STEPS 1000
            INCONFS_PER_SEARCH 0
            CONFSEARCH_TORSION_SAMPLING Enhanced
            CONFSEARCH_METHOD lmod
            CONFORMER_ELIMINATION_VALUE 0.5
            FORCE_FIELD OPLS_2005
            ELECTROSTATIC_TREATMENT Constant dielectric
            JOBTYPE CONFSEARCH
            ENERGY_WINDOW 21.0
            DIELECTRIC_CONSTANT 1
            CHARGES_FROM Force field
            USE_SUBSTRUCTURE_FILE True
            CONFSEARCH_STEPS_PER_ROTATABLE 50
            RETAIN_MIRROR_IMAGE True
            """)

        with io.BytesIO() as stream:
            ifile = ConfSearchInput(
                confsearch_method=ConfSearchMethod.lmod,
                confsearch_torsion_sampling=ConfSearchTorsionSampling.enhanced)
            ifile.write(stream, maefile='1AQ1_pv.mae')

            self.assertMultiLineEqual(expected, stream.getvalue())

    def test_energy_default_parameters(self):
        expected = textwrap.dedent("""\
            INPUT_STRUCTURE_FILE 1AQ1_pv.mae
            CUTOFF Extended
            FORCE_FIELD OPLS_2005
            SOLVENT GB/SA
            USE_SUBSTRUCTURE_FILE True
            ELECTROSTATIC_TREATMENT Constant dielectric
            ENERGY_REPORT_OPTION FULLREPORT
            DIELECTRIC_CONSTANT 1
            CHARGES_FROM Force field
            JOBTYPE ENERGY_LISTING
            """)

        with io.BytesIO() as stream:
            ifile = EnergyInput()
            ifile.write(stream, maefile='1AQ1_pv.mae')

            self.assertMultiLineEqual(expected, stream.getvalue())

    def test_energy_assigned_parameters(self):
        expected = textwrap.dedent("""\
            INPUT_STRUCTURE_FILE 1AQ1_pv.mae
            CUTOFF Extended
            FORCE_FIELD OPLS_2005
            SOLVENT GB/SA
            USE_SUBSTRUCTURE_FILE True
            ELECTROSTATIC_TREATMENT Constant dielectric
            ENERGY_REPORT_OPTION MMOFILE
            DIELECTRIC_CONSTANT 1
            CHARGES_FROM Force field
            JOBTYPE ENERGY_LISTING
            """)

        with io.BytesIO() as stream:
            ifile = EnergyInput(
                energy_report_option=EnergyReportOption.mmofile)
            ifile.write(stream, maefile='1AQ1_pv.mae')

            self.assertMultiLineEqual(expected, stream.getvalue())

if __name__ == '__main__':
    unittest.main()
