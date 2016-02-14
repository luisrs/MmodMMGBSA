import re

from fatools.core_ext import builtin
from fatools.utils.kernel import InvalidArgumentError, MissingArgumentError

CRITERIA_OPTION_REGEX = re.compile(r'^(m(?:in|ax))_(.+)')


# TODO add docstring
class InteractionCriteria(object):
    def __init__(self, **kwargs):
        self._measures = InteractionCriteria._extract_options(kwargs)
    measures = property(lambda self: self._measures.copy())

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:  # cascade up to raise appropriate exception
            return super(InteractionCriteria, self).__getattribute__(name)

    def __getitem__(self, item):
        if item not in self._measures and item[4:] not in self._measures:
            raise KeyError(item)
        if item.startswith('min_') or item.startswith('max_'):
            prefix, measure = item.split('_', 1)
            return self._measures[measure][0 if prefix == 'min' else 1]
        return tuple(self._measures[item])

    def match_interaction(self, interaction):
        return self.match_measurements(**interaction.measurements)

    def match_measurements(self, **kwargs):
        for measure in self._measures:
            if measure not in kwargs:
                err_template = 'missing required \'{name}\' measurement'
                raise MissingArgumentError(measure, err_template)
        return all(self._match_constraints(measure, value)
                   for measure, value in kwargs.items()
                   if value is not None)

    def replace(self, **kwargs):
        opts = InteractionCriteria._extract_options(kwargs, default='')
        measures = self.measures.transform_values(list)  # implicit copy
        for name, minmax in opts.items():
            if name not in measures:
                continue
            for i, new_value in enumerate(minmax):
                if new_value is not '':
                    measures[name][i] = new_value
        return self.__class__(**measures.transform_values(tuple))

    @staticmethod
    def _extract_options(kwargs, default=None):
        opts = dict()
        for measure, value in kwargs.items():
            match = CRITERIA_OPTION_REGEX.match(measure)
            if match is not None:
                prefix, measure = match.group(1), match.group(2)
                if measure not in opts:
                    opts[measure] = [default, default]
                opts[measure][0 if prefix == 'min' else 1] = value
            elif isinstance(value, tuple) and len(value) == 2:  # (min, max)
                opts[measure] = value
            else:
                raise InvalidArgumentError(measure, value)
        return opts.transform_values(tuple, copy=False)

    def _match_constraints(self, measure, value):
        min_value, max_value = self[measure]
        if min_value is None:
            return value <= max_value
        elif max_value is None:
            return value >= min_value
        return min_value <= value <= max_value
