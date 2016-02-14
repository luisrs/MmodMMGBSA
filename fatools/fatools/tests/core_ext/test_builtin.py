import unittest

from fatools.core_ext import builtin


class DictTests(unittest.TestCase):
    def test_transform_values(self):
        mapping = dict(cpu=1, host='localhost', debug=False)
        expected = dict(cpu='1', host='localhost', debug='False')
        self.assertDictEqual(expected, mapping.transform_values(str))

if __name__ == '__main__':
    unittest.main()
