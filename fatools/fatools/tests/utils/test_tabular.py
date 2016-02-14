import copy
import StringIO
import textwrap
import unittest

from fatools.utils.tabular import Table
from fatools.utils.text import glued


class TableTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = dict()
        cls.data['planets'] = [
            ['Planet', 'R (km)', 'mass (x 10^29 kg)'],
            ['Sun', 696000, 1989100000],
            ['Earth', 6371, 5973.6],
            ['Moon', 1737, 73.5],
            ['Mars', 3390, 641.85]]
        cls.maxDiff = None

    def test_adding_multiple_rows(self):
        table = Table(colwidths=(5, 6, 10))
        table.addrows(TableTests.data['planets'][1:])
        expected = textwrap.dedent("""\
            -------  --------  ------------
            Sun        696000    1.9891e+09
            Earth        6371        5973.6
            Moon         1737          73.5
            Mars         3390        641.85
            -------  --------  ------------
            """)
        self.assertMultiLineEqual(expected, str(table))

    def test_creation_with_column_width_less_than_header_length(self):
        table = Table(colwidths=(1, 5, 2), headers=('123456', '1234', '12'))
        self.assertEqual(6, table.cols[0].width)
        self.assertEqual(5, table.cols[1].width)
        self.assertEqual(2, table.cols[2].width)

    def test_creation_with_column_width_less_than_one(self):
        with self.assertRaises(ValueError) as err:
            Table(colwidths=(0, 4))
        self.assertEqual('invalid column width: 0', str(err.exception))

        with self.assertRaises(ValueError) as err:
            Table(colwidths=(2, -1))
        self.assertEqual('invalid column width: -1', str(err.exception))

    def test_creation_with_unbalanced_widths_and_headers(self):
        with self.assertRaises(ValueError) as err:
            Table(colwidths=(1, 2, 3, 4), headers=('1', '2', '3', '4', '5'))
        self.assertEqual('invalid column width: None', str(err.exception))

    def test_table_live_update(self):
        output = StringIO.StringIO()
        table = Table(colwidths=(5, 6, 10), write_on_data=True, outfile=output)
        self.assertEqual('', output.getvalue())

        expected = [
            '-------  --------  ------------\n',
            'Sun        696000    1.9891e+09\n',
            'Earth        6371        5973.6\n',
            'Moon         1737          73.5\n',
            'Mars         3390        641.85\n',
            '-------  --------  ------------\n']

        table.start_editing()
        self.assertMultiLineEqual(expected[0], output.getvalue())

        for i, row in enumerate(TableTests.data['planets'][1:]):
            table.addrow(row)
            self.assertMultiLineEqual(
                glued(expected[:2 + i]), output.getvalue())

        table.end_editing()
        self.assertMultiLineEqual(glued(expected), output.getvalue())

    def test_table_live_update_with_multiple_rows(self):
        output = StringIO.StringIO()
        table = Table(colwidths=(5, 6, 10), write_on_data=True, outfile=output)
        self.assertEqual('', output.getvalue())

        expected = [
            '-------  --------  ------------\n',
            'Sun        696000    1.9891e+09\n',
            'Earth        6371        5973.6\n',
            'Moon         1737          73.5\n',
            'Mars         3390        641.85\n',
            '-------  --------  ------------\n']

        table.start_editing()
        self.assertMultiLineEqual(expected[0], output.getvalue())

        table.addrows(TableTests.data['planets'][1:])
        self.assertMultiLineEqual(glued(expected[:-1]), output.getvalue())

        table.end_editing()
        self.assertMultiLineEqual(glued(expected), output.getvalue())

    def test_table_with_alignments(self):
        table = Table(colwidths=(5, 6, 10),
                      colaligns=('right', 'left', 'left'))
        for row in TableTests.data['planets'][1:]:
            table.addrow(row)
        expected = textwrap.dedent(
            '-------  --------  ------------\n'
            '    Sun  696000    1.9891e+09  \n'
            '  Earth  6371      5973.6      \n'
            '   Moon  1737      73.5        \n'
            '   Mars  3390      641.85      \n'
            '-------  --------  ------------\n')
        self.assertMultiLineEqual(expected, str(table))

    def test_table_with_custom_format_on_one_column(self):
        table = Table(colwidths=(5, 6, 7))
        table.columns[2].format_type = '.1e'
        for row in TableTests.data['planets'][1:]:
            table.addrow(row)
        expected = textwrap.dedent("""\
            -------  --------  ---------
            Sun        696000    2.0e+09
            Earth        6371    6.0e+03
            Moon         1737    7.4e+01
            Mars         3390    6.4e+02
            -------  --------  ---------
            """)
        self.assertMultiLineEqual(expected, str(table))

    def test_table_with_custom_formats(self):
        table = Table(colwidths=(5, 12, 7),
                      colformats=('', '.2%', '.1e'))
        for row in TableTests.data['planets'][1:]:
            table.addrow(row)
        expected = textwrap.dedent("""\
            -------  --------------  ---------
            Sun        69600000.00%    2.0e+09
            Earth        637100.00%    6.0e+03
            Moon         173700.00%    7.4e+01
            Mars         339000.00%    6.4e+02
            -------  --------------  ---------
            """)
        self.assertMultiLineEqual(expected, str(table))

    def test_table_with_custom_formats_by_type(self):
        table = Table(colwidths=(5, 12, 7), colformats=('', '.2%', '.1e'))
        table.cols[-1].formats[str] = '^{width}'

        data = copy.deepcopy(TableTests.data['planets'][1:])
        data[2][-1] = 'small'
        table.addrows(data)

        expected = (
            '-------  --------------  ---------\n',
            'Sun        69600000.00%    2.0e+09\n',
            'Earth        637100.00%    6.0e+03\n',
            'Moon         173700.00%    small  \n',
            'Mars         339000.00%    6.4e+02\n',
            '-------  --------------  ---------\n')
        self.assertMultiLineEqual(glued(expected), str(table))

    def test_table_with_headers(self):
        table = Table(colwidths=(6, 6, 17),
                      headers=TableTests.data['planets'][0])
        for row in TableTests.data['planets'][1:]:
            table.addrow(row)
        expected = textwrap.dedent(
            'Planet    R (km)    mass (x 10^29 kg)  \n'
            '--------  --------  -------------------\n'
            'Sun         696000           1.9891e+09\n'
            'Earth         6371               5973.6\n'
            'Moon          1737                 73.5\n'
            'Mars          3390               641.85\n'
            '--------  --------  -------------------\n')
        self.assertMultiLineEqual(expected, str(table))

    def test_table_with_placeholder(self):
        table = Table(colwidths=(5, 6, 10), placeholder='unknown')

        data = copy.deepcopy(TableTests.data['planets'][1:])
        data[1][1] = data[-1][2] = None
        table.addrows(data)

        expected = (
            '-------  --------  ------------\n',
            'Sun        696000    1.9891e+09\n',
            'Earth    unknown         5973.6\n',
            'Moon         1737          73.5\n',
            'Mars         3390  unknown     \n',
            '-------  --------  ------------\n')
        self.assertMultiLineEqual(glued(expected), str(table))

    def test_table_with_style_default(self):
        table = Table(colwidths=(5, 6, 10))
        for row in TableTests.data['planets'][1:]:
            table.addrow(row)
        expected = textwrap.dedent("""\
            -------  --------  ------------
            Sun        696000    1.9891e+09
            Earth        6371        5973.6
            Moon         1737          73.5
            Mars         3390        641.85
            -------  --------  ------------
            """)
        self.assertMultiLineEqual(expected, str(table))

    def test_table_with_style_plain(self):
        table = Table(colwidths=(5, 6, 10), style='plain')
        for row in TableTests.data['planets'][1:]:
            table.addrow(row)
        expected = textwrap.dedent("""\
            Sun    696000  1.9891e+09
            Earth    6371      5973.6
            Moon     1737        73.5
            Mars     3390      641.85
            """)
        self.assertMultiLineEqual(expected, str(table))

if __name__ == '__main__':
    unittest.main()
