# -*- coding: utf-8 -*-

"""Functions to deal with string inflection.

It singularizes and pluralizes English words, and transforms strings from
CamelCase to underscored_string.

\* Adaptation from ``inflection`` module created by Janne Vanhala available at
`GitHub <https://github.com/jpvanhal/inflection>`_.

"""
import re
import unicodedata

PLURALS = [
    (r'(?i)(quiz)$', r'\1zes'),
    (r'(?i)^(oxen)$', r'\1'),
    (r'(?i)^(ox)$', r'\1en'),
    (r'(?i)(m|l)ice$', r'\1ice'),
    (r'(?i)(m|l)ouse$', r'\1ice'),
    (r'(?i)(matr|vert|ind)(?:ix|ex)$', r'\1ices'),
    (r'(?i)(x|ch|ss|sh)$', r'\1es'),
    (r'(?i)([^aeiouy]|qu)y$', r'\1ies'),
    (r'(?i)(hive)$', r'\1s'),
    (r'(?i)([lr])f$', r'\1ves'),
    (r'(?i)([^f])fe$', r'\1ves'),
    (r'(?i)sis$', 'ses'),
    (r'(?i)([ti])a$', r'\1a'),
    (r'(?i)([ti])um$', r'\1a'),
    (r'(?i)(buffal|tomat)o$', r'\1oes'),
    (r'(?i)(bu)s$', r'\1ses'),
    (r'(?i)(alias|status)$', r'\1es'),
    (r'(?i)(octop|vir)i$', r'\1i'),
    (r'(?i)(octop|vir)us$', r'\1i'),
    (r'(?i)^(ax|test)is$', r'\1es'),
    (r'(?i)s$', 's'),
    (r'$', 's')]

SINGULARS = [
    (r'(?i)(database)s$', r'\1'),
    (r'(?i)(quiz)zes$', r'\1'),
    (r'(?i)(matr)ices$', r'\1ix'),
    (r'(?i)(vert|ind)ices$', r'\1ex'),
    (r'(?i)^(ox)en', r'\1'),
    (r'(?i)(alias|status)(es)?$', r'\1'),
    (r'(?i)(octop|vir)(us|i)$', r'\1us'),
    (r'(?i)^(a)x[ie]s$', r'\1xis'),
    (r'(?i)(cris|test)(is|es)$', r'\1is'),
    (r'(?i)(shoe)s$', r'\1'),
    (r'(?i)(o)es$', r'\1'),
    (r'(?i)(bus)(es)?$', r'\1'),
    (r'(?i)(m|l)ice$', r'\1ouse'),
    (r'(?i)(x|ch|ss|sh)es$', r'\1'),
    (r'(?i)(m)ovies$', r'\1ovie'),
    (r'(?i)(s)eries$', r'\1eries'),
    (r'(?i)([^aeiouy]|qu)ies$', r'\1y'),
    (r'(?i)([lr])ves$', r'\1f'),
    (r'(?i)(tive)s$', r'\1'),
    (r'(?i)(hive)s$', r'\1'),
    (r'(?i)([^f])ves$', r'\1fe'),
    (r'(?i)(t)he(sis|ses)$', r'\1hesis'),
    (r'(?i)(s)ynop(sis|ses)$', r'\1ynopsis'),
    (r'(?i)(p)rogno(sis|ses)$', r'\1rognosis'),
    (r'(?i)(p)arenthe(sis|ses)$', r'\1arenthesis'),
    (r'(?i)(d)iagno(sis|ses)$', r'\1iagnosis'),
    (r'(?i)(b)a(sis|ses)$', r'\1asis'),
    (r'(?i)(a)naly(sis|ses)$', r'\1nalysis'),
    (r'(?i)([ti])a$', r'\1um'),
    (r'(?i)(n)ews$', r'\1ews'),
    (r'(?i)(ss)$', r'\1'),
    (r'(?i)s$', '')]

UNCOUNTABLES = {'equipment', 'fish', 'information', 'jeans', 'money', 'rice',
                'series', 'sheep', 'species'}


def add_irregular(singular, plural):
    """Add an irregular word to the register.

    A convenience function to add appropriate rules to plurals and singular
    for irregular words.

    """
    def caseinsensitive(string):
        return ''.join('[' + char + char.upper() + ']' for char in string)

    if singular[0].upper() == plural[0].upper():
        PLURALS.insert(0, (
            r"(?i)(%s)%s$" % (singular[0], singular[1:]),
            r'\1' + plural[1:]))
        PLURALS.insert(0, (
            r"(?i)(%s)%s$" % (plural[0], plural[1:]),
            r'\1' + plural[1:]))
        SINGULARS.insert(0, (
            r"(?i)(%s)%s$" % (plural[0], plural[1:]),
            r'\1' + singular[1:]))
    else:
        PLURALS.insert(0, (
            r"%s%s$" % (singular[0].upper(), caseinsensitive(singular[1:])),
            plural[0].upper() + plural[1:]))
        PLURALS.insert(0, (
            r"%s%s$" % (singular[0].lower(), caseinsensitive(singular[1:])),
            plural[0].lower() + plural[1:]))
        PLURALS.insert(0, (
            r"%s%s$" % (plural[0].upper(), caseinsensitive(plural[1:])),
            plural[0].upper() + plural[1:]))
        PLURALS.insert(0, (
            r"%s%s$" % (plural[0].lower(), caseinsensitive(plural[1:])),
            plural[0].lower() + plural[1:]))
        SINGULARS.insert(0, (
            r"%s%s$" % (plural[0].upper(), caseinsensitive(plural[1:])),
            singular[0].upper() + singular[1:]))
        SINGULARS.insert(0, (
            r"%s%s$" % (plural[0].lower(), caseinsensitive(plural[1:])),
            singular[0].lower() + singular[1:]))


def camelize(sentence, upcase_first_letter=True):
    """Convert a string into *CamelCase* form.

    :func:`camelize` can be though as an inverse of :func:`underscore`,
    although there are some cases where that does not hold::

        >>> camelize(underscore("IOError"))
        "IoError"

    Parameters
    ----------
    sentence : str
        A sentence to camelize.
    upcase_first_letter : bool, optional
        If True, then the first letter is capitalized; it's downcased
        otherwise. Defaults to True.

    Returns
    -------
    str
        A camelized string.

    Examples
    --------
    >>> camelize("device_type")
    "DeviceType"
    >>> camelize("device_type", False)
    "deviceType"

    """
    camelized = re.sub(r'(?:^|_)(.)', lambda m: upcase(m.group(1)), sentence)
    if not upcase_first_letter:
        return inflect(camelized, downcase, only_characters_at=0)
    return camelized


def capitalize(sentence):
    """Functional form for string's :meth:`capitalize` method."""
    return sentence.capitalize()


def dasherize(word):
    """Replace underscores with dashes in a word.

    Examples
    --------
    >>> dasherize('puni_puni')
    'puni-puni'

    """
    return word.replace('_', '-')


def downcase(sentence):
    """Functional form for string's :meth:`lower` method."""
    return sentence.lower()


def humanize(word, capitalized=True, acronyms=()):
    """Transform an underscored string into a human readable form.

    Capitalize the first word and turn underscores into spaces and strip a
    trailing ``'_id'``, if any. Like :func:`titleize`, this is meant for
    creating pretty output.

    Acronyms can be given to preserve correct case folding in such cases.

    Parameters
    ----------
    word : str
        String to humanize.
    capitalized : bool, optional
        If True, the resulting string will be capitalized, otherwise the first
        letter will be in lowercase. Defaults to True.
    acronyms : tuple, optional
        A tuple of acronyms with correct case folding to be preserved.
        Defaults to an empty tuple.

    Returns
    -------
    str
        A humanized version of the given string.

    Examples
    --------
    >>> humanize('employee_salary')
    'Employee salary'
    >>> humanize('author_id')
    'Author'
    >>> humanize('author_id', capitalized=False)
    'author'
    >>> humanize('ssl_error', acronyms=('SSL',))
    'SSL error'

    """
    word = re.sub(r'_id$', '', word)
    word = word.replace('_', ' ')
    word = re.sub(r'(?i)([a-z\d]*)', lambda m: m.group(1).lower(), word)
    word = capitalize(word) if capitalized else word
    for acronym in acronyms:
        word = re.sub(r'(?i){}'.format(acronym), acronym, word)
    return word


def inflect(sentence, inflector, only_characters_at=None):
    """Transform a string into the desired form.

    Parameters
    ----------
    sentence : str
        A string to inflect.
    inflector : callable object
        A callable object that transform a string into the desired form.
    only_characters_at : int or tuple of int or slice, optional
        If given, only characters located at the given indexes are transformed.
        Defaults to None (flag for all characters).

    Returns
    -------
    str
        A inflected version of the given sentence.

    Raises
    ------
    TypeError
        If the given indexes are not an integer, tuple, list, slice or None.

    Examples
    --------
    >>> inflect('UPCASE LONG SENTENCE', downcase)
    'upcase long sentence'
    >>> inflect('UPCASE LONG SENTENCE', downcase, only_characters_at=10)
    'UPCASE LONg SENTENCE'
    >>> inflect('UPCASE LONG SENTENCE', downcase,
    ...         only_characters_at=slice(6, 18))
    'UPCASE long sentenCE'

    """
    if isinstance(only_characters_at, int):
        index = slice(only_characters_at, only_characters_at + 1)
    elif isinstance(only_characters_at, (list, tuple)):
        index = slice(*only_characters_at)
    elif only_characters_at is None:
        index = slice(0, len(sentence))
    elif isinstance(only_characters_at, slice):
        index = only_characters_at
    else:
        raise TypeError('`inflect` expected a slice for only_characters_at '
                        'argument, got {}'.format(only_characters_at))
    if index.start is None:  # slice(i) -> slice(None, i, None)
        index = slice(0, index.stop)

    inflected = inflector(sentence[index])
    return sentence[:index.start] + inflected + sentence[index.stop:]


def normalize(sentence):
    """Shorthand for `parameterize(sentence, '_')`."""
    return parameterize(sentence, '_')


def ordinal(num):
    """Return the suffix used to denote the position in an ordered sequence.

    Parameters
    ----------
    num : int or str
        A natural number (positive integer not including zero).

    Returns
    -------
    str
        Suffix denoting number position (one of ``'st'``, ``'nd'``, ``'rd'``,
        ``'th'``).

    Raises
    ------
    ValueError
        If the given number is not a positive integer (zero not included).

    Examples
    --------
    >>> ordinal(1)
    'st'
    >>> ordinal(2)
    'nd'
    >>> ordinal(1002)
    'nd'
    >>> ordinal(1003)
    'rd'
    >>> ordinal(0)
    Traceback (most recent call last):
      ...
    ValueError: `ordinal` expected a natural number, got 0
    >>> ordinal(-6)
    Traceback (most recent call last):
      ...
    ValueError: `ordinal` expected a natural number, got -6

    """
    num = int(num)
    if num <= 0:
        raise ValueError('`ordinal` expected a natural number, got %s' % num)
    if num % 100 in (11, 12, 13):
        return 'th'
    return {1: 'st', 2: 'nd', 3: 'rd'}.get(num % 10, 'th')


def ordinalize(num):
    """Return an ordinal string for the given number.

    Used to denote the position in an ordered sequence such as 1st, 2nd, 3rd,
    4th and so on.

    Parameters
    ----------
    num : int or str
        A natural number (positive integer not including zero).

    Returns
    -------
    str
        An ordinal string (``'1st'``, ``'4th'``, etc).

    Examples
    --------
    >>> ordinalize(1)
    '1st'
    >>> ordinalize(2)
    '2nd'
    >>> ordinalize(1002)
    '1002nd'
    >>> ordinalize(1003)
    '1003rd'

    """
    return '{}{}'.format(num, ordinal(num))


def parameterize(sentence, sep='-'):
    """Return a safe representation with a given word separator.

    It replaces special characters to avoid encoding problems by using
    :func:`transliterate`, then it transforms the resulting sentence into a
    lower case form and removes whitespace by replacing it with the given
    separator.

    Examples
    --------
    >>> parameterize('Donald E. Knuth')
    'donald-e-knuth'
    >>> parameterize('Random text with *(bad)* characters')
    'random_text_with_bad_characters'
    >>> parameterize('Random text with *(bad)* characters', '|')
    'random|text|with|bad|characters'

    """
    sentence = transliterate(sentence)
    # Turn unwanted chars into the separator
    sentence = re.sub(r'(?i)[^a-z0-9\-_]+', sep, sentence)
    if sep:
        re_sep = re.escape(sep)
        # No more than one of the separator in a row.
        sentence = re.sub(r'%s{2,}' % re_sep, sep, sentence)
        # Remove leading/trailing separator.
        sentence = re.sub(r'(?i)^{0}|{0}$'.format(re_sep), '', sentence)
    return downcase(sentence)


def pluralize(word, count=None):
    """Return the plural form of a word.

    Parameters
    ----------
    word : str
        Word to pluralize.
    count : int, optional
        If given, pluralize the word only if ``count`` is not equal to 1,
        otherwise returns its singular form instead. Defaults to None.

    Returns
    -------
    str
        Pluralized form unless ``count`` is 1; singular form otherwise.

    Examples
    --------
    >>> pluralize('post')
    'posts'
    >>> pluralize('octopus')
    'octopi'
    >>> pluralize('sheep')
    'sheep'
    >>> pluralize('CamelOctopus')
    'CamelOctopi'
    >>> pluralize('octopus', count=1)
    'octopus'
    >>> pluralize('octopus', count=10)
    'octopi'

    """
    if not word or word.lower() in UNCOUNTABLES:
        return word
    if count == 1:
        return singularize(word)
    for rule, replacement in PLURALS:
        if re.search(rule, word):
            return re.sub(rule, replacement, word)
    return word


def singularize(word):
    """Return the singular form of a word, the reverse of :func:`pluralize`.

    Examples
    --------
    >>> singularize('posts')
    'post'
    >>> singularize('octopi')
    'octopus'
    >>> singularize('sheep')
    'sheep'
    >>> singularize('word')
    'word'
    >>> singularize('CamelOctopi')
    'CamelOctopus'

    """
    for inflection in UNCOUNTABLES:
        if re.search(r'(?i)\b(%s)\Z' % inflection, word):
            return word

    for rule, replacement in SINGULARS:
        if re.search(rule, word):
            return re.sub(rule, replacement, word)
    return word


def titleize(sentence):
    """Return a pretty representation of the sentence suitable for titles.

    It capitalizes all the words and replace some characters in the string to
    create a nicer looking title.

    Examples
    --------
    >>> titleize('man from the boondocks')
    'Man From The Boondocks'
    >>> titleize('x-men: the last stand')
    'X Men: The Last Stand'
    >>> titleize('TheManWithoutAPast')
    'The Man Without A Past'
    >>> titleize('raiders_of_the_lost_ark')
    'Raiders Of The Lost Ark'

    """
    return re.sub(r'\b(\'?[a-z])',
                  lambda m: m.group(1).capitalize(),
                  humanize(underscore(sentence)))


def transliterate(word):
    """Replace non-ASCII characters with an ASCII approximation.

    If no approximation exists, the non-ASCII character is ignored.

    Examples
    --------
    >>> transliterate('älämölö')
    'alamolo'
    >>> transliterate('Ærøskøbing')
    'rskbing'

    """
    normalized = unicodedata.normalize('NFKD', word)
    return normalized.encode('ascii', 'ignore').decode('ascii')


def upcase(sentence):
    """Functional form for string's :meth:`upper` method."""
    return sentence.upper()


def underscore(sentence):
    """Make an underscored, lowercase form from the sentence.

    Examples
    --------
    >>> underscore('DeviceType')
    'device_type'

    As a rule of thumb you can think of :func:`underscore` as the inverse of
    :func:`camelize`, though there are cases where that does not hold:

    >>> camelize(underscore('IOError'))
    'IoError'

    """
    sentence = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', sentence)
    sentence = re.sub(r'([a-z\d])([A-Z])', r'\1_\2', sentence)
    sentence = sentence.replace('-', '_')
    # added
    sentence = sentence.replace(' ', '_')
    return downcase(sentence)

add_irregular('person', 'people')
add_irregular('man', 'men')
add_irregular('child', 'children')
add_irregular('sex', 'sexes')
add_irregular('move', 'moves')
add_irregular('cow', 'kine')
add_irregular('zombie', 'zombies')
