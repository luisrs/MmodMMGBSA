import unittest
from fatools.utils.text import glued, pad, to_sentence


class GluedTests(unittest.TestCase):
    def test_glued(self):
        self.assertEqual('0123456789', glued(range(10)))

    def test_glued_with_custom_converter(self):
        self.assertEqual(
            '0,1,4,9,16,25,36,49,64,81',
            glued(range(10), ',', converter=lambda i: str(i**2)))

    def test_glued_with_custom_separator(self):
        self.assertEqual('0|1|2|3|4|5|6|7|8|9', glued(range(10), '|'))


class PadTests(unittest.TestCase):
    def test_pad_with_alignment_center(self):
        self.assertEqual(
            '  this is a string  ',
            pad('this is a string', 20, align='^'))

    def test_pad_with_alignment_center_and_unequal_fill_width(self):
        self.assertEqual(
            ' this is a string  ',
            pad('this is a string', 19, align='^'))

    def test_pad_with_alignment_right(self):
        self.assertEqual(
            '    this is a string',
            pad('this is a string', 20, align='>'))

    def test_pad_with_bad_alignment(self):
        with self.assertRaisesRegexp(ValueError, 'invalid alignment'):
            pad('this is a string', 20, align='top')

    def test_pad_with_fillchar(self):
        self.assertEqual(
            'this is a string----',
            pad('this is a string', 20, fillchar='-'))

    def test_pad_with_width(self):
        self.assertEqual(
            'this is a string    ',
            pad('this is a string', 20))

    def test_pad_with_width_less_than_length(self):
        self.assertEqual(
            'this is a string',
            pad('this is a string', 10))


class SentenceTests(unittest.TestCase):
    def setUp(self):
        self.words = ['one', 'two', 'three']

    def test_empty(self):
        self.assertEqual('', to_sentence([]))

    def test_one_element(self):
        self.assertEqual('one', to_sentence(self.words[:1]))

    def test_two_elements(self):
        self.assertEqual('one and two', to_sentence(self.words[:2]))

    def test_more_than_two_elements(self):
        self.assertEqual('one, two and three', to_sentence(self.words[:3]))

    def test_custom_connector(self):
        sentence = to_sentence(self.words, sep='; ')
        self.assertEqual('one; two and three', sentence)

    def test_custom_two_word_connector(self):
        sentence = to_sentence(self.words[:2], two_words_sep=' or ')
        self.assertEqual('one or two', sentence)

    def test_custom_last_word_connector(self):
        sentence = to_sentence(self.words[:3], last_word_sep=' or ')
        self.assertEqual('one, two or three', sentence)

    def test_custom_word_and_last_word_connector(self):
        sentence = to_sentence(self.words[:3], sep=' or ',
                               last_word_sep=' or at least ')
        self.assertEqual('one or two or at least three', sentence)

    def test_converter(self):
        sentence = to_sentence(self.words, converter=lambda word: word[0])
        self.assertEqual('o, t and t', sentence)

if __name__ == '__main__':
    unittest.main()
