import unittest
from fatools.application.schrodinger.jaguar import RunJaguarCmd


class CmdTests(unittest.TestCase):
    def test_creation_with_non_default_options(self):
        cmd = RunJaguarCmd('jag_scan-r_6-31Gsspp_System.in', ncpu=4,
                           jobname='jag01')
        expected = ('jaguar run -TPP 4 -jobname jag01 '
                    'jag_scan-r_6-31Gsspp_System.in')
        self.assertEqual(expected, str(cmd))

    def test_creation_with_one_file(self):
        cmd = RunJaguarCmd('jag-sp-midix-EPJ.in')
        expected = ('jaguar run -TPP 1 jag-sp-midix-EPJ.in')
        self.assertEqual(expected, str(cmd))

if __name__ == '__main__':
    unittest.main()
