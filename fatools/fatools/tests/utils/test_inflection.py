# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import unittest
from functools import partial
from fatools.utils import inflection


SINGULAR_TO_PLURAL = (
    ('search', 'searches'),
    ('switch', 'switches'),
    ('fix', 'fixes'),
    ('box', 'boxes'),
    ('process', 'processes'),
    ('address', 'addresses'),
    ('case', 'cases'),
    ('stack', 'stacks'),
    ('wish', 'wishes'),
    ('fish', 'fish'),
    ('jeans', 'jeans'),
    ('funky jeans', 'funky jeans'),

    ('category', 'categories'),
    ('query', 'queries'),
    ('ability', 'abilities'),
    ('agency', 'agencies'),
    ('movie', 'movies'),

    ('archive', 'archives'),

    ('index', 'indices'),

    ('wife', 'wives'),
    ('safe', 'saves'),
    ('half', 'halves'),

    ('move', 'moves'),

    ('salesperson', 'salespeople'),
    ('person', 'people'),

    ('spokesman', 'spokesmen'),
    ('man', 'men'),
    ('woman', 'women'),

    ('basis', 'bases'),
    ('diagnosis', 'diagnoses'),
    ('diagnosis_a', 'diagnosis_as'),

    ('datum', 'data'),
    ('medium', 'media'),
    ('stadium', 'stadia'),
    ('analysis', 'analyses'),

    ('node_child', 'node_children'),
    ('child', 'children'),

    ('experience', 'experiences'),
    ('day', 'days'),

    ('comment', 'comments'),
    ('foobar', 'foobars'),
    ('newsletter', 'newsletters'),

    ('old_news', 'old_news'),
    ('news', 'news'),

    ('series', 'series'),
    ('species', 'species'),

    ('quiz', 'quizzes'),

    ('perspective', 'perspectives'),

    ('ox', 'oxen'),
    ('photo', 'photos'),
    ('buffalo', 'buffaloes'),
    ('tomato', 'tomatoes'),
    ('dwarf', 'dwarves'),
    ('elf', 'elves'),
    ('information', 'information'),
    ('equipment', 'equipment'),
    ('bus', 'buses'),
    ('status', 'statuses'),
    ('status_code', 'status_codes'),
    ('mouse', 'mice'),

    ('louse', 'lice'),
    ('house', 'houses'),
    ('octopus', 'octopi'),
    ('virus', 'viri'),
    ('alias', 'aliases'),
    ('portfolio', 'portfolios'),

    ('vertex', 'vertices'),
    ('matrix', 'matrices'),
    ('matrix_fu', 'matrix_fus'),

    ('axis', 'axes'),
    ('testis', 'testes'),
    ('crisis', 'crises'),

    ('rice', 'rice'),
    ('shoe', 'shoes'),

    ('horse', 'horses'),
    ('prize', 'prizes'),
    ('edge', 'edges'),

    ('cow', 'kine'),
    ('database', 'databases'))

CAMEL_TO_UNDERSCORE = (
    ('Product',               'product'),
    ('SpecialGuest',          'special_guest'),
    ('ApplicationController', 'application_controller'),
    ('Area51Controller',      'area51_controller'))

CAMEL_TO_UNDERSCORE_WITHOUT_REVERSE = (
    ('HTMLTidy',              'html_tidy'),
    ('HTMLTidyGenerator',     'html_tidy_generator'),
    ('FreeBSD',               'free_bsd'),
    ('HTML',                  'html'))

STRING_TO_PARAMETERIZED = (
    ('Donald E. Knuth', 'donald-e-knuth'),
    ('Random text with *(bad)* characters', 'random-text-with-bad-characters'),
    ('Allow_Under_Scores', 'allow_under_scores'),
    ('Trailing bad characters!@#', 'trailing-bad-characters'),
    ('!@#Leading bad characters', 'leading-bad-characters'),
    ('Squeeze   separators', 'squeeze-separators'),
    ('Test with + sign', 'test-with-sign'),
    ('Test with malformed utf8 \251', 'test-with-malformed-utf8'))

STRING_TO_PARAMETERIZE_WITH_NO_SEPARATOR = (
    ('Donald E. Knuth', 'donaldeknuth'),
    ('With-some-dashes', 'with-some-dashes'),
    ('Random text with *(bad)* characters', 'randomtextwithbadcharacters'),
    ('Trailing bad characters!@#', 'trailingbadcharacters'),
    ('!@#Leading bad characters', 'leadingbadcharacters'),
    ('Squeeze   separators', 'squeezeseparators'),
    ('Test with + sign', 'testwithsign'),
    ('Test with malformed utf8 \251', 'testwithmalformedutf8'))

STRING_TO_PARAMETERIZE_WITH_UNDERSCORE = (
    ('Donald E. Knuth', 'donald_e_knuth'),
    ('Random text with *(bad)* characters', 'random_text_with_bad_characters'),
    ('With-some-dashes', 'with-some-dashes'),
    ('Retain_underscore', 'retain_underscore'),
    ('Trailing bad characters!@#', 'trailing_bad_characters'),
    ('!@#Leading bad characters', 'leading_bad_characters'),
    ('Squeeze   separators', 'squeeze_separators'),
    ('Test with + sign', 'test_with_sign'),
    ('Test with malformed utf8 \251', 'test_with_malformed_utf8'))

STRING_TO_PARAMETERIZED_AND_NORMALIZED = (
    ('Malmö', 'malmo'),
    ('Garçons', 'garcons'),
    ('Ops\331', 'opsu'),
    ('Ærøskøbing', 'rskbing'),
    ('Aßlar', 'alar'),
    ('Japanese: 日本語', 'japanese'))

UNDERSCORE_TO_HUMAN = (
    ('employee_salary',       'Employee salary'),
    ('employee_id',           'Employee'),
    ('underground',           'Underground'))

MIXTURE_TO_TITLEIZED = (
    ('active_record',         'Active Record'),
    ('ActiveRecord',          'Active Record'),
    ('action web service',    'Action Web Service'),
    ('Action Web Service',    'Action Web Service'),
    ('Action web service',    'Action Web Service'),
    ('actionwebservice',      'Actionwebservice'),
    ('Actionwebservice',      'Actionwebservice'),
    ('david\'s code',          'David\'s Code'),
    ('David\'s code',          'David\'s Code'),
    ('david\'s Code',          'David\'s Code'))

ORDINAL_NUMBERS = (
    ('1', '1st'),
    ('2', '2nd'),
    ('3', '3rd'),
    ('4', '4th'),
    ('5', '5th'),
    ('6', '6th'),
    ('7', '7th'),
    ('8', '8th'),
    ('9', '9th'),
    ('10', '10th'),
    ('11', '11th'),
    ('12', '12th'),
    ('13', '13th'),
    ('14', '14th'),
    ('20', '20th'),
    ('21', '21st'),
    ('22', '22nd'),
    ('23', '23rd'),
    ('24', '24th'),
    ('100', '100th'),
    ('101', '101st'),
    ('102', '102nd'),
    ('103', '103rd'),
    ('104', '104th'),
    ('110', '110th'),
    ('111', '111th'),
    ('112', '112th'),
    ('113', '113th'),
    ('1000', '1000th'),
    ('1001', '1001st'))

UNDERSCORES_TO_DASHES = (
    ('street',                'street'),
    ('street_address',        'street-address'),
    ('person_street_address', 'person-street-address'))


class PluralizationTests(unittest.TestCase):
    def test_pluralize_empty_string(self):
        self.assertEqual('', inflection.pluralize(''))

    def test_pluralize_plurals(self):
        self.assertEqual('plurals', inflection.pluralize('plurals'))
        self.assertEqual('Plurals', inflection.pluralize('Plurals'))

    def test_pluralize_plural(self):
        for singular, plural in SINGULAR_TO_PLURAL:
            self.assertEqual(plural, inflection.pluralize(plural))
            self.assertEqual(plural.capitalize(),
                             inflection.pluralize(plural.capitalize()))

    def test_pluralize_singular(self):
        for singular, plural in SINGULAR_TO_PLURAL:
            self.assertEqual(plural, inflection.pluralize(singular))
            self.assertEqual(plural.capitalize(),
                             inflection.pluralize(singular.capitalize()))

    def test_pluralize_with_count(self):
        self.assertEqual('post', inflection.pluralize('post', count=1))
        self.assertEqual('post', inflection.pluralize('posts', count=1))
        self.assertEqual('posts', inflection.pluralize('post', count=2))
        self.assertEqual('posts', inflection.pluralize('posts', count=2))
        self.assertEqual('posts', inflection.pluralize('post', count=0))
        self.assertEqual('posts', inflection.pluralize('posts', count=0))

    def test_singularize_plural(self):
        for singular, plural in SINGULAR_TO_PLURAL:
            self.assertEqual(singular, inflection.singularize(plural))
            self.assertEqual(singular.capitalize(),
                             inflection.singularize(plural.capitalize()))

    def test_uncountability(self):
        for word in inflection.UNCOUNTABLES:
            self.assertEqual(word, inflection.singularize(word))
            self.assertEqual(word, inflection.pluralize(word))
            self.assertEqual(inflection.pluralize(word),
                             inflection.singularize(word))

    def test_uncountable_word_is_not_greedy(self):
        uncountable_word = 'ors'
        countable_word = 'sponsor'

        inflection.UNCOUNTABLES.add(uncountable_word)
        try:
            self.assertEqual(uncountable_word,
                             inflection.singularize(uncountable_word))
            self.assertEqual(uncountable_word,
                             inflection.pluralize(uncountable_word))
            self.assertEqual(inflection.pluralize(uncountable_word),
                             inflection.singularize(uncountable_word))

            self.assertEqual('sponsor', inflection.singularize(countable_word))
            self.assertEqual('sponsors', inflection.pluralize(countable_word))
            self.assertEqual(
                'sponsor',
                inflection.singularize(inflection.pluralize(countable_word)))
        finally:
            inflection.UNCOUNTABLES.remove(uncountable_word)


class CaseTests(unittest.TestCase):
    def test_camelize(self):
        for camel, underscore in CAMEL_TO_UNDERSCORE:
            self.assertEqual(camel, inflection.camelize(underscore))

    def test_camelize_with_lower_downcases_the_first_letter(self):
        self.assertEqual('capital', inflection.camelize('Capital', False))
        self.assertEqual('deviceType',
                         inflection.camelize('device_type', False))

    def test_camelize_with_underscores(self):
        self.assertEqual('CamelCase', inflection.camelize('Camel_Case'))

    def test_humanize(self):
        for underscore, human in UNDERSCORE_TO_HUMAN:
            self.assertEqual(human, inflection.humanize(underscore))

    def test_humanize_no_capitalized(self):
        for underscore, human in UNDERSCORE_TO_HUMAN:
            self.assertEqual(
                human[0].lower() + human[1:],
                inflection.humanize(underscore, capitalized=False))

    def test_humanize_with_acronym(self):
        self.assertEqual(
            'SSL error',
            inflection.humanize('ssl_error', acronyms=('SSL',)))

    def test_titleize(self):
        for before, titleized in MIXTURE_TO_TITLEIZED:
            self.assertEqual(titleized, inflection.titleize(before))


class ParameterizeTests(unittest.TestCase):
    def test_parameterize(self):
        for sentence, parameterized in STRING_TO_PARAMETERIZED:
            self.assertEqual(parameterized, inflection.parameterize(sentence))

    def test_parameterize_and_normalize(self):
        for sentence, parameterized in STRING_TO_PARAMETERIZED_AND_NORMALIZED:
            self.assertEqual(parameterized, inflection.parameterize(sentence))

    def test_parameterize_with_custom_separator(self):
        for sentence, parameterized in STRING_TO_PARAMETERIZE_WITH_UNDERSCORE:
            self.assertEqual(parameterized,
                             inflection.parameterize(sentence, '_'))

    def test_parameterize_with_multi_character_separator(self):
        for sentence, parameterized in STRING_TO_PARAMETERIZED:
            self.assertEqual(parameterized.replace('-', '__sep__'),
                             inflection.parameterize(sentence, '__sep__'))

    def test_parameterize_with_no_separator(self):
        test_data = STRING_TO_PARAMETERIZE_WITH_NO_SEPARATOR
        for sentence, parameterized in test_data:
            self.assertEqual(parameterized,
                             inflection.parameterize(sentence, ''))


class OrdinalTests(unittest.TestCase):
    def test_ordinal(self):
        for number, ordinalized in ORDINAL_NUMBERS:
            self.assertEqual(ordinalized, number + inflection.ordinal(number))

    def test_ordinalize(self):
        for number, ordinalized in ORDINAL_NUMBERS:
            self.assertEqual(ordinalized, inflection.ordinalize(number))


class InflectionTests(unittest.TestCase):
    def test_dasherize(self):
        for sentence, dasherized in UNDERSCORES_TO_DASHES:
            self.assertEqual(dasherized, inflection.dasherize(sentence))

    def test_inflect(self):
        inflect = partial(inflection.inflect, inflector=inflection.downcase)
        self.assertEqual('titleized long sentence',
                         inflect('Titleized Long Sentence'))
        self.assertEqual('capitalized long sentence',
                         inflect('Capitalized Long Sentence'))
        self.assertEqual('downcase long sentence',
                         inflect('downcase Long Sentence'))
        self.assertEqual('upcase long sentence',
                         inflect('UPCASE LONG SENTENCE'))
        self.assertEqual('random case sentence',
                         inflect('RAnDom cAsE SenteNcE'))

    def test_inflect_with_index(self):
        inflect = partial(inflection.inflect, inflector=inflection.downcase)
        self.assertEqual(
            'UPCASE LONg SENTENCE',
            inflect('UPCASE LONG SENTENCE', only_characters_at=10))
        self.assertEqual(
            'upcase lonG SENTENCE',
            inflect('UPCASE LONG SENTENCE', only_characters_at=slice(10)))
        self.assertEqual(
            'upcase lonG SENTENCE',
            inflect('UPCASE LONG SENTENCE', only_characters_at=(10,)))
        self.assertEqual(
            'UPCASE long sentenCE',
            inflect('UPCASE LONG SENTENCE', only_characters_at=slice(6, 18)))
        self.assertEqual(
            'UPCASE long sentenCE',
            inflect('UPCASE LONG SENTENCE', only_characters_at=(6, 18)))

        with self.assertRaises(TypeError):
            inflect('sentence', only_characters_at='a')

if __name__ == '__main__':
    unittest.main()
