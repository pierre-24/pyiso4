import unittest
from typing import Any

from pyiso4.lexer import Lexer, TokenType
from pyiso4.ltwa import Pattern, Abbreviate
from pyiso4.normalize_string import normalize, Level, number_of_ligatures


class TestNormalize(unittest.TestCase):
    """Test the unicode normalization"""

    def test_normalize(self) -> None:
        tests = [
            ('test', 'test'),
            ('abbréviation', 'abbreviation'),
            ('ačaruli', 'acaruli'),
            ('għall', 'ghall'),
            ('chrysopœia', 'chrysopoeia'),
            ("Côte-d'Azur", "Cote-d'Azur")
        ]

        for inp, out in tests:
            self.assertEqual(out, normalize(inp, Level.NORMAL))

    def test_normalize_extra(self) -> None:
        tests = [
            ('TeSt', 'test'),
            ("Côte-d'Azur", 'cote d azur')
        ]

        for inp, out in tests:
            self.assertEqual(out, normalize(inp, Level.HARD))

    def test_ligatures(self) -> None:
        self.assertEqual(number_of_ligatures('test'), 0)
        self.assertEqual(number_of_ligatures('coeur'), 0)
        self.assertEqual(number_of_ligatures('cœur'), 1)


class TestLexer(unittest.TestCase):
    def test_stopword(self) -> None:
        stopwords = ['x', 'y']
        text = ' '.join(stopwords)

        # no stopword
        tokens = list(Lexer(text, []).tokenize())
        for t in tokens[:-1]:  # skip EOS
            self.assertEqual(t.type, TokenType.WORD)

        # all stopwords
        tokens = list(Lexer(text, stopwords).tokenize())
        for t in tokens[:-1]:  # skip EOS
            self.assertEqual(t.type, TokenType.STOPWORD)

    def test_token_position(self) -> None:
        text = 'this is a test-case for you'
        for t in Lexer(text, []).tokenize():
            if t.position >= 0:
                self.assertEqual(text[t.position], t.value[0])

    def test_hyphenated_words(self) -> None:
        cpd1 = 'état'
        cpd2 = 'nation'
        text = '{}-{}'.format(cpd1, cpd2)
        tokens = list(Lexer(text, []).tokenize())
        self.assertEqual(tokens[0].type, TokenType.WORD)
        self.assertEqual(tokens[0].value, cpd1)
        self.assertEqual(tokens[1].type, TokenType.HYPHEN)
        self.assertEqual(tokens[2].type, TokenType.WORD)
        self.assertEqual(tokens[2].value, cpd2)

    def test_surname_as_abbreviation(self) -> None:
        abbrv = 'A.'
        text = 'Legacy of {} Einstein'.format(abbrv)
        tokens = list(Lexer(text, ['of']).tokenize())

        self.assertEqual(len(tokens), 5)  # four words + EOS
        self.assertEqual(tokens[2].type, TokenType.ABBREVIATION)
        self.assertEqual(tokens[2].value, abbrv)


class TestPattern(unittest.TestCase):
    def test_pattern_match(self) -> None:
        text = 'abc'

        # no dash
        pattern_without_dash = Pattern.from_line('{}\tx\tmul'.format(text))
        self.assertTrue(pattern_without_dash.match(pattern_without_dash.pattern))
        self.assertFalse(pattern_without_dash.match(text + 'x'))  # x is not an inflection!
        self.assertFalse(pattern_without_dash.match(text[:-1]))
        self.assertFalse(pattern_without_dash.match(text.replace('a', 'b')))

        # dash in the middle (not a wildcard)
        pattern_with_dash = Pattern.from_line('{}\tx\tmul'.format(text.replace('b', '-')))
        self.assertTrue(pattern_with_dash.match(pattern_with_dash.pattern))
        self.assertFalse(pattern_with_dash.match(text))
        self.assertFalse(pattern_with_dash.match(text + 'x'))
        self.assertFalse(pattern_with_dash.match(text[:-1]))
        self.assertFalse(pattern_with_dash.match(text.replace('a', 'b')))

        # a ending dash (is a wildcard)
        pattern_with_ending_dash = Pattern.from_line('abc-\tx\tmul')
        self.assertTrue(pattern_with_ending_dash.match(text))
        self.assertTrue(pattern_with_ending_dash.match(text + 'x'))
        self.assertFalse(pattern_with_ending_dash.match(text[:-1]))
        self.assertFalse(pattern_with_ending_dash.match(text.replace('a', 'b')))

        # check infliction
        word = 'rabbit'
        pattern = Pattern.from_line('{}\tn.a.\teng'.format(word))
        self.assertTrue(pattern.match(word))
        self.assertTrue(pattern.match(word + 's'))  # plural form
        self.assertFalse(pattern.match(word + 'x'))  # not an inflexion

    def test_patter_match_on_sentence(self) -> None:
        # no dash
        text = 'abc'
        pattern_without_dash = Pattern.from_line('{}\tx\tmul'.format(text))
        self.assertTrue(pattern_without_dash.match('{} is the beginning'.format(text)))
        self.assertTrue(pattern_without_dash.match('{}-xyz is the alphabet'.format(text)))  # `-` is a BOUNDARY

        # a ending dash (is a wildcard)
        pattern_with_ending_dash = Pattern.from_line('abc-\tx\tmul')
        self.assertTrue(pattern_with_ending_dash.match('{} is the beginning'.format(text)))
        self.assertTrue(pattern_with_ending_dash.match('{}ef is the beginning'.format(text)))

        # pattern with space
        text = 'united kingdom'
        pattern_with_space = Pattern.from_line('{}\tu.k.\ten'.format(text))
        self.assertTrue(pattern_with_space.match('{} of of Great Britain and Northern Ireland'.format(text)))


class TestAbbreviate(unittest.TestCase):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.abbreviate = Abbreviate.create()

    def test_abbreviations(self) -> None:
        with open('tests/tests.tsv') as f:
            for line in f.readlines():
                fields = line.split('\t')
                self.assertEqual(fields[1].strip(), self.abbreviate(fields[0].strip(), remove_part=True))
