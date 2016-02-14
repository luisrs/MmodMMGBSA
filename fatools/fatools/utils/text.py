from fatools.utils.enum import Enum
from fatools.utils.kernel import reraise, suppress


class TextAlignment(Enum):
    left = '<'
    right = '>'
    center = '^'
    natural = ''

    @classmethod
    def translate(cls, align):
        with suppress(KeyError):
            return cls[align]
        try:
            return cls(align)
        except ValueError as err:
            reraise(err, 'invalid alignment: {}', repr(align))


# TODO add docstring
def excerpt(text, nlines=20):
    if nlines is None:
        return text
    lines = text.split('\n')
    return glued(lines[:nlines] if nlines > 0 else lines[nlines:], '\n')


def glued(iterable, sep='', converter=str):
    """Concatenate an iterable with given separator.

    Each element is converted to a string representation, and then joined
    together by the given separator (an empty string is used by default).

    Parameters
    ----------
    iterable : iterable object
        An iterable object.
    sep : str, optional
        Separator string. Defaults to empty string (``''``).
    converter : callable object, optional
        A callable object that takes an element and returns a string
        representation.
        Defaults to :func:`str` function.

    Examples
    --------
    >>> from fatools.utils.text import glued
    >>> glued(range(10))
    '0123456789'
    >>> glued(range(10), '|')
    '0|1|2|3|4|5|6|7|8|9'
    >>> glued(range(5), ' ', converter=lambda i: format(i, '.2e'))
    '0.00e+00 1.00e+00 2.00e+00 3.00e+00 4.00e+00'

    """
    return sep.join(map(converter, iterable))
concatenate = glued


# TODO add `multiline` option
def pad(text, width, align='left', fillchar=''):
    """Add padding to the given string.

    Parameters
    ----------
    text : str
        A string to be padding.
    width : int
        Minimum field width. If it's less than the `text`'s length,
        this function just returns `text` as is.
    align : {'left', '<', 'right', '>', 'center', '^'}
        Text alignment within the specified width. Acceptable values are
        ``left`` or ``<``, ``right`` or ``>``, and ``center`` or ``^``.
        Default to ``left``.
    fillchar : str, optional
        One-sized string or character to use as padding.
        Defaults to empty string (space).

    Raises
    ------
    ValueError
        If ``align`` is not a valid alignment value.

    Examples
    --------
    >>> from fatools.utils.text import pad
    >>> pad('this is a string', 20)
    'this is a string    '
    >>> pad('this is a string', 10)
    'this is a string'
    >>> pad('this is a string', 20, align='>')
    '    this is a string'
    >>> pad('this is a string', 20, align='^')
    '  this is a string  '
    >>> pad('this is a string', 20, align='top')
    Traceback (most recent call last):
      ...
    ValueError: invalid alignment: 'top'
    >>> pad('this is a string', 20, fillchar='-')
    'this is a string----'

    """
    alignment = TextAlignment.translate(align).value
    return format(text, '{}{}{}'.format(fillchar, alignment, width))


def to_sentence(words, sep=', ', two_words_sep=' and ', last_word_sep=' and ',
                converter=str):
    """Convert an iterable into a comma-separated sentence.

    This function considers the following cases:
    When `words` is empty, an empty string is returned.
    If `words` contains only one element, such element is returned.
    If `words` contains two elements, they are concatenated by `two_words_sep`.
    Finally, if `words` has three or more elements, they are joined by
    `sep` except for the last element, which will be preceded by
    `last_word_sep` instead.
    In all cases, `converter` is called for each element to ensure a string
    representation.

    Parameters
    ----------
    words : iterable object
        An iterable object.
    sep : str, optional
        The sign or word used to join the three or more elements.
        Defaults to ``', '``.
    two_words_sep : str, optional
        The sign or word used to join the two elements.
        Defaults to ``' and '``.
    last_word_sep : str, optional
        The sign or word used to join the last element when there is three or
        more elements.
        Defaults to ``' and '``.
    converter : callable object, optional
        A callable object that takes an element and returns a string
        representation.
        Defaults to :func:`str` function.

    Returns
    -------
    str
        A comma-separated sentence based on the given elements.

    Examples
    --------
    >>> from fatools.utils.text import to_sentence
    >>> to_sentence([])
    ''
    >>> to_sentence(['one'])
    'one'
    >>> to_sentence(['one', 'two', 'three'])
    'one, two and three'
    >>> to_sentence(['one', 'two', 'three'], last_word_sep=' or ')
    'one, two or three'
    >>> to_sentence(['one', 'two', 'three'], sep=' or ', last_word_sep=' or ')
    'one or two or three'
    >>> to_sentence(['one', 'two', 'three'], converter=str.upper)
    'ONE, TWO and THREE'

    """
    words, length = tuple(map(converter, words)), len(words)
    if length == 0:
        return ''
    elif length == 1:
        return words[0]
    elif length == 2:
        return glued(words, two_words_sep)
    else:
        return glued(words[:-1], sep) + last_word_sep + words[-1]
