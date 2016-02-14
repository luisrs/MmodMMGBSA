"""Pretty-print tabular data.
"""

from __future__ import print_function

import io
from collections import namedtuple
from itertools import izip_longest
from numbers import Number

from fatools.utils.enum import Enum
from fatools.utils.text import TextAlignment, glued

TableStyleOptions = namedtuple(
    'TableStyleOptions',
    ('padding', 'spacing',
     'border_top', 'border_right', 'border_bottom', 'border_left',
     'header_hline'))


# TODO add functionality for creating custom styles
class TableStyle(Enum):
    simple = TableStyleOptions(
        padding=2,
        spacing=2,
        border_top='-',
        border_right=None,
        border_bottom='-',
        border_left=None,
        header_hline='-')
    plain = TableStyleOptions(
        padding=0,
        spacing=2,
        border_top=None,
        border_right=None,
        border_bottom=None,
        border_left=None,
        header_hline=None)
    condensed = TableStyleOptions(
        padding=0,
        spacing=1,
        border_top=None,
        border_right=None,
        border_bottom=None,
        border_left=None,
        header_hline='-')
    default = simple


class TableColumn(object):
    def __init__(self, width, header=None, align=None, format_type=None):
        self.header = header
        self.width = width
        self.align = align
        self.format_type = format_type
        self.formats = dict()

    @property
    def align(self):
        return self._align

    @align.setter
    def align(self, value):
        self._align = TextAlignment.translate(value or '')

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, value):
        if not isinstance(value, int) or value < 1:
            raise ValueError('invalid column width: ' + str(value))
        if self.header is not None and value < len(self.header):
            value = len(self.header)
        self._width = value

    def format_spec_for_type(self, dtype, padding=0, default_formats=None):
        if dtype in self.formats:  # custom format by type
            return '{{:{}}}'.format(self.formats[dtype].format(
                width=self.width + padding,
                align=self.align))
        format_type = self.format_type
        if format_type is None:
            if default_formats is not None and dtype in default_formats:
                format_type = default_formats[dtype]
            else:
                format_type = 'g' if issubclass(dtype, Number) else ''
        return '{{:{}{}{}}}'.format(
            self.align.value, self.width + padding, format_type)


# TODO add docstring
# TODO add functional form with automatic column width calculation
class Table(object):
    def __init__(self, colwidths, headers=(), colaligns=(), colformats=(),
                 style='default', placeholder=None,
                 write_on_data=False, outfile=None):
        self._columns = Table._construct_columns(
            colwidths, headers, colaligns, colformats)
        self.style = TableStyle[style].value  # TableStyle enum instance
        self.placeholder = placeholder

        self._templates = dict()
        self._rows = []

        self.write_on_data = write_on_data
        self.outfile = outfile
    columns = cols = property(lambda self: self._columns)
    has_footer = property(lambda self: self.style.border_bottom is not None)
    is_empty = property(lambda self: not self._rows)
    ncols = property(lambda self: len(self.columns))

    def __str__(self):
        with io.BytesIO() as iostream:
            self.write(iostream)
            return iostream.getvalue()

    @property
    def headers(self):
        if self.columns[0].header is None:
            return None
        return tuple(col.header for col in self.columns)

    def addrow(self, row):
        self._rows.append(row)
        if self.write_on_data is True:
            self._write_row(self.outfile, row)

    def addrows(self, rows):
        self._rows.extend(rows)
        if self.write_on_data is True:
            start = len(self._rows) - len(rows)
            for row in self._rows[start:]:
                self._write_row(self.outfile, row)

    def end_editing(self):
        self._write_footer(self.outfile)

    def start_editing(self):
        self._write_header(self.outfile)

    def write(self, outfile=None):
        outfile = outfile or self.outfile
        if outfile is None:
            raise IOError('no file passed as output')
        self._write_header(outfile, )
        for row in self._rows:
            self._write_row(outfile, row)
        self._write_footer(outfile, )

    @classmethod
    def _construct_columns(cls, widths, headers, aligns, formats):
        col_it = izip_longest(widths, headers, aligns, formats, fillvalue=None)
        return tuple(TableColumn(width, header, align, tformat)
                     for width, header, align, tformat in col_it)

    def _construct_template_with_types(self, dtypes):
        format_specs = []
        for j, dtype in enumerate(dtypes):
            format_specs.append(self.columns[j].format_spec_for_type(
                dtype, self.style.padding))
        return glued(format_specs, ' ' * self.style.spacing)

    def _write_footer(self, outfile):
        if self.style.border_bottom is not None:
            self._write_hline(outfile, self.style.border_bottom)

    def _write_header(self, outfile):
        headers = self.headers
        if headers is not None:
            template = self._get_template_for_types((str,) * len(headers))
            print(template.format(*headers), file=outfile)
        if self.style.header_hline:
            self._write_hline(outfile, self.style.header_hline)

    def _write_hline(self, outfile, character):
        dividers = []
        for col in self.columns:
            dividers.append(character * (col.width + self.style.padding))
        print(glued(dividers, ' ' * self.style.spacing), file=outfile)

    def _write_row(self, outfile, row):
        types = tuple(type(val) for val in row)
        template = self._get_template_for_types(types)
        if self.placeholder is not None and None in row:
            row = tuple(c if c is not None else self.placeholder for c in row)
        print(template.format(*row), file=outfile)

    def _get_template_for_types(self, types):
        if types not in self._templates:
            template = self._construct_template_with_types(types)
            self._templates[types] = template
        return self._templates[types]
