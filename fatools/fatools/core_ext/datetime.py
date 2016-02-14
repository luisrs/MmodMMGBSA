from __future__ import absolute_import

from collections import namedtuple
from datetime import timedelta

from fatools.utils.kernel import extend_class
from fatools.utils.inflection import pluralize
from fatools.utils.text import glued, to_sentence


TimedeltaComponents = namedtuple('TimedeltaComponents',
                                 'weeks days hours minutes seconds')


@extend_class(timedelta, name='components')
@property
def _timedelta_components(self):
    """Return a tuple with (weeks, days, hours, minutes, seconds)."""
    return TimedeltaComponents(
        self.days / 7,
        self.days,
        int(self.seconds / 3600.),
        int(self.seconds % 3600 / 60.),
        int(self.seconds % 3600 % 60))


# TODO add docstring
@extend_class(timedelta, name='format')
def _timedelta_format(self, format_spec='long', limit=None):
    if format_spec == 'short':
        limit = 2

    sep = '' if format_spec == 'short' else ' '
    tokens = []
    for component, value in self.components._asdict().items():
        if value == 0:
            continue
        component = component[0] if format_spec == 'short' else \
            pluralize(component, count=value)
        tokens.append('{}{}{}'.format(value, sep, component))
        if limit is not None and len(tokens) >= limit:
            break
    if not tokens:
        return '0s' if format_spec == 'short' else '0 seconds'
    if format_spec == 'short':
        return glued(tokens, ' ')
    return to_sentence(tokens)
