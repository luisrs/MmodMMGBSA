import csv
import re
from collections import Counter
from functools import partial
from itertools import product

import matplotlib as mpl
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import numpy as np
from fatools.core_ext import builtin
from fatools.structutils.interactions import curate_interactions
from fatools.structutils.interactions.interaction import interaction_abbr
from fatools.utils.caching import cached_property
from fatools.utils.kernel import InvalidArgumentError
from fatools.utils.inflection import add_irregular, pluralize
from fatools.utils.text import glued, pad

builtin.extend_tuple()
builtin.extend_list()

add_irregular('cation-pi', 'cation-pi')
add_irregular('pi-pi', 'pi-pi')

IFP_BIN_WIDTH = 8
IFP_LABEL_WIDTH = 10

make_colomap = mpl.colors.LinearSegmentedColormap.from_list
IFP_COLOR_SCHEMES = {
    'h-bond': make_colomap('Blues', [(0, 'w'), (1, 'b')]),
    'steric-clash': make_colomap('Oranges', [(0, 'w'), (1, 'orange')]),
    'pi-pi': make_colomap('Cyans', [(0, 'w'), (1, 'c')]),
    'cation-pi': make_colomap('Greens', [(0, 'w'), (1, 'g')]),
    'x-bond': make_colomap('Purples', [(0, 'w'), (1, 'purple')]),
    'salt-bridge': make_colomap('Purples', [(0, 'w'), (1, 'brown')])
}


class InteractionFingerprint(object):
    def __init__(self, bins_desc, bins):
        self._bins_desc = bins_desc.freeze()
        self._bins = bins.freeze()

    interaction_names = cached_property(lambda self: self._bins_desc.pluck(0))

    def __iter__(self):
        return iter(self._bins)

    def __len__(self):
        return len(self._bins)

    def __str__(self):
        return self._printable

    @cached_property
    def description(self):
        return glued((self._printable_header, self._printable), '\n')

    @classmethod
    def encode_interactions(cls, interactions, bins_desc=None):
        interactions = curate_interactions(interactions)
        bins_desc_and_values = interactions.map(_encode_interaction)

        # one residue fragment may establish more than one interaction of the
        # same kind; in that case, choose the "better" one.
        bins_desc = bins_desc or bins_desc_and_values.pluck(0).uniq()
        bins_desc_and_values_map = dict(
            (key, group.pluck(1))
            for key, group in bins_desc_and_values.group_by('0'))
        bins = list.with_capacity(len(bins_desc))
        for i, bin_desc in enumerate(bins_desc):
            if bin_desc in bins_desc_and_values_map:
                bins[i] = min(bins_desc_and_values_map[bin_desc])
        return cls(bins_desc, bins)

    @cached_property
    def _formatted_bins(self):
        def formatter(iname, val):
            return format(val, '.0%') if iname == 'steric-clash' else val

        return tuple(formatter(iname, val) if val is not None else ''
                     for iname, val in zip(self.interaction_names, self._bins))

    @cached_property
    def _printable(self):
        return glued([pad(val, IFP_BIN_WIDTH) for val in self._formatted_bins])

    @cached_property
    def _printable_header(self):
        residues, i_descriptions = [], []
        for iname, resnum, rescode, f_desc in self._bins_desc:
            residue = rescode + str(resnum)
            residues.append(residue if residue not in residues else '')
            iabbr = interaction_abbr(iname)
            i_descriptions.append('{}:{}'.format(iabbr, f_desc))

        formatter = lambda val: pad(val, IFP_BIN_WIDTH)
        header = glued(residues.map(formatter)) + '\n'
        header += glued(i_descriptions.map(formatter))
        return header


class InteractionFingerprintMatrix(object):
    def __init__(self, interaction_matrix, labels=None):
        self._bins_desc = _gather_bins_desc(interaction_matrix)
        ifp_encode = partial(InteractionFingerprint.encode_interactions,
                             bins_desc=self._bins_desc)
        self._fingerprints = interaction_matrix.map(ifp_encode).freeze()

        if labels is not None:
            labels = labels.map(str.strip).freeze()
            width = max(labels.map(len)) + 2
            self._label_width = max(width, IFP_LABEL_WIDTH)
        self._labels = labels

    labels = property(lambda self: self._labels)
    nbins = property(lambda self: len(self._bins_desc))

    def __getitem__(self, item):
        return self._fingerprints[item]

    def __len__(self):
        return len(self._fingerprints)

    def __str__(self):
        return self._printable

    @cached_property
    def description(self):
        return glued((self._printable_header, self._printable), '\n')

    def write_csv(self, filepath):
        with open(filepath, 'wb') as csvfile:
            csvwriter = csv.writer(csvfile)

            for line in self[0]._printable_header.split('\n'):
                row = re.findall(r'.{%s}' % IFP_BIN_WIDTH, line).map(str.strip)
                if self.labels:
                    row.insert(0, '')
                csvwriter.writerow(row)
            for i, ifp in enumerate(self._fingerprints):
                row = list(ifp._formatted_bins)
                if self.labels:
                    row.insert(0, self.labels[i])
                csvwriter.writerow(row)

    def write_img(self, filepath, dpi=150, group_by='residue'):
        if group_by == 'residue':
            writer = _PerResidueIFPImgWriter
        elif group_by == 'interaction':
            writer = _PerInteractionIFPImgWriter
        else:
            raise InvalidArgumentError('group_by', group_by)
        writer.write(filepath, self, dpi)

    @cached_property
    def _normalized_matrix(self):
        iranges = self._get_interaction_ranges()

        matrix = list.with_capacity(len(self), self.nbins, repeated_value=-1)
        for i, ifp in enumerate(self._fingerprints):
            for j, value in tuple(enumerate(ifp._bins)).exclude(None, key=1):
                iname = ifp._bins_desc[j][0]
                minv, maxv = iranges[iname]
                try:
                    if iname == 'steric-clash':
                        matrix[i][j] = (value - minv) / (maxv - minv)
                    else:  # shorter distance is better
                        matrix[i][j] = (value - maxv) / (minv - maxv)
                except ZeroDivisionError:  # min and max values are the same
                    matrix[i][j] = 1  # interaction only appears once
        return matrix

    @cached_property
    def _printable(self):
        formatter = lambda _, ifp: str(ifp)
        if self.labels:  # add label at the start of each line
            pad_label = partial(pad, width=self._label_width)
            formatter = lambda i, ifp: pad_label(self.labels[i]) + str(ifp)
        return glued(self._fingerprints.map_with_index(formatter), '\n')

    @property
    def _printable_header(self):
        headers = self._fingerprints[0]._printable_header.split('\n')
        if self.labels:  # add spacing/title at the start of each header line
            for i in range(len(headers) - 1):
                headers[i] = ' ' * self._label_width + headers[i]
            headers[-1] = pad('Entry', self._label_width) + headers[-1]
        return glued(headers, '\n')

    def _get_interaction_ranges(self):
        iranges = dict((i, []) for i in self._bins_desc.pluck(0).uniq())
        for ifp in self._fingerprints:
            for bin_desc, value in zip(ifp._bins_desc, ifp._bins):
                iranges[bin_desc[0]].append(value)
        for iname, values in iranges.items():
            values = values.compact()  # remove None elements
            iranges[iname] = (min(values), max(values))
        return iranges


class _PerInteractionIFPImgWriter(object):
    @staticmethod
    def populate_subplot(ax, g_bins_desc, matrix, j_offset):
        iname = g_bins_desc[0][0]
        for i, j in product(range(len(matrix)), range(len(g_bins_desc))):
            value = matrix[i][j + j_offset] * .8 + .2
            color = IFP_COLOR_SCHEMES[iname](value)
            rt = plt.Rectangle([j, i],
                               width=1,
                               height=1,
                               facecolor=color,
                               edgecolor=color)
            ax.add_patch(rt)

    @staticmethod
    def setup_grid(ifp):
        plt.subplots(figsize=(ifp.nbins, (len(ifp) + .5) * .35))
        icounts = Counter(ifp._bins_desc.pluck(0).sorted())
        ratios = [icounts[i] for i in ifp._bins_desc.pluck(0).uniq().sorted()]
        return gridspec.GridSpec(1, len(ratios), width_ratios=ratios)

    @staticmethod
    def setup_matrix(ifp):
        bins_desc = ifp._bins_desc.sorted_by(0, 1)
        columns = list.with_capacity(ifp.nbins)
        for bin_desc, col in zip(ifp._bins_desc, zip(*ifp._normalized_matrix)):
            j = bins_desc.index(bin_desc)
            columns[j] = col
        return bins_desc, np.array(zip(*columns))

    @staticmethod
    def setup_subplot(grid, gi, bins_desc):
        ax = plt.subplot(grid[gi])
        ax.invert_yaxis()

        xlabels = ['{}{} {}'.format(rescode, resnum, frag)
                   for _, resnum, rescode, frag in bins_desc]
        plt.xticks(np.arange(0.5, len(xlabels) + 0.5), xlabels)
        ax.xaxis.set_tick_params(top='off',
                                 labeltop='on',
                                 bottom='off',
                                 labelbottom='off',
                                 labelsize='small')
        ax.text(len(bins_desc) / 2.,
                -.65,
                pluralize(bins_desc[0][0].title()),
                horizontalalignment='center',
                verticalalignment='baseline',
                fontsize='large',
                fontweight='bold')

        if gi == 0:
            ax.yaxis.set_tick_params(top='off', bottom='off')
        else:
            ax.yaxis.set_tick_params(top='off',
                                     bottom='off',
                                     labelbottom='off')
        return ax

    @staticmethod
    def write(filepath, ifp, dpi=150):
        all_bins_desc, matrix = _PerInteractionIFPImgWriter.setup_matrix(ifp)
        grid, gi = _PerInteractionIFPImgWriter.setup_grid(ifp), 0
        j_offset = 0
        for iname, bins_desc in all_bins_desc.group_by(0):
            ax = _PerInteractionIFPImgWriter.setup_subplot(grid, gi, bins_desc)
            if gi == 0:
                plt.yticks(np.arange(0.5, len(ifp) + 0.5), ifp.labels)
            _PerInteractionIFPImgWriter.populate_subplot(
                ax, bins_desc, matrix, j_offset)
            ax.autoscale_view()
            j_offset += len(bins_desc)
            gi += 1
        plt.tight_layout(pad=2, h_pad=0, w_pad=0)
        plt.savefig(filepath, dpi=dpi)


class _PerResidueIFPImgWriter(object):
    @staticmethod
    def write(filepath, ifp, dpi=150):
        matrix = ifp._normalized_matrix
        axes = _PerResidueIFPImgWriter._setup_plot_for(ifp)

        for i, j in product(range(len(ifp)), range(ifp.nbins)):
            iname = ifp._bins_desc[j][0]
            value = matrix[i][j] * .8 + .2  # start at a darker color
            color = IFP_COLOR_SCHEMES[iname](value)
            rt = plt.Rectangle([j, i], 1, 1, facecolor=color, edgecolor=color)
            axes.add_patch(rt)
        axes.autoscale_view()
        axes.invert_yaxis()

        plt.tight_layout()
        plt.savefig(filepath, dpi=dpi)

    @staticmethod
    def _setup_plot_for(ifp):
        xlabels, displayed_inames = [], []
        for resnum, rescode, frag in ifp._bins_desc.pluck(1, 2, 3):
            res = rescode + str(resnum)
            if res in displayed_inames:
                res = ''
            displayed_inames.append(res)
            xlabels.append(glued((res, frag), '\n'))

        fig, axes = plt.subplots(figsize=(ifp.nbins * .65, len(ifp) * .35))
        plt.xticks(np.arange(0.5, ifp.nbins + 0.5), xlabels)
        plt.yticks(np.arange(0.5, len(ifp) + 0.5), ifp.labels)
        axes.xaxis.set_tick_params(top='off',
                                   labeltop='on',
                                   bottom='off',
                                   labelbottom='off')
        axes.yaxis.set_tick_params(top='off', bottom='off')
        return axes


def _encode_interaction(interaction):
    try:
        residue, fragment = interaction.recep_desc.split(' ')
    except ValueError:  # does not have a fragment description
        residue, fragment = interaction.recep_desc, ''
    rescode, resnum = residue[0], int(residue[1:])
    info = (interaction.name, resnum, rescode, fragment)
    measure = 'distance' if interaction.name != 'steric-clash' else \
        'relative_overlap'
    return info, float(format(getattr(interaction, measure), '.3g'))


def _gather_bins_desc(interaction_matrix):
    interactions = interaction_matrix.flatten().sorted_by(
        'residues[0]', 'name', 'atom_indexes')
    return interactions.map(_encode_interaction).pluck('0').uniq()
