import unittest

from pyiso4.lexer import Lexer, TokenType
from pyiso4.ltwa import Pattern, Abbreviate
from pyiso4.normalize_string import normalize, Level


class TestNormalize(unittest.TestCase):
    """Test the unicode normalization"""

    def test_normalize(self):
        tests = [
            ('test', 'test'),
            ('abbréviation', 'abbreviation'),
            ('ačaruli', 'acaruli'),
            ('għall', 'ghall'),
            ('chrysopœia', 'chrysopoeia'),
            ('Côte-d\'Azur', 'Cote-d\'Azur')
        ]

        for inp, out in tests:
            self.assertEqual(out, normalize(inp, Level.NORMAL))

    def test_normalize_extra(self):
        tests = [
            ('TeSt', 'test'),
            ('Côte-d\'Azur', 'cote d azur')
        ]

        for inp, out in tests:
            self.assertEqual(out, normalize(inp, Level.HARD))


class TestLexer(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def test_stopword(self):
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

    def test_token_position(self):
        text = 'this is a test'
        for t in Lexer(text, []).tokenize():
            if t.position >= 0:
                self.assertEqual(text[t.position], t.value[0])


class TestPattern(unittest.TestCase):
    def test_pattern_match(self):
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


class TestAbbreviate(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.abbreviate = Abbreviate.from_files('LTWA_20170914-modified.csv', 'stopwords.txt')

    def test_abbreviations(self):
        with open('tests/tests.csv') as f:
            for l in f.readlines():
                fields = l.split('\t')
                self.assertEqual(fields[1].strip(), self.abbreviate(fields[0].strip(), remove_part=True))
