import unittest
import sys

from pyiso4.ltwa import Pattern
from pyiso4.ltwa import Abbreviate


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
            self.assertEqual(out, Pattern.normalize(inp))

    def test_normalize_extra(self):
        tests = [
            ('TeSt', 'test'),
            ('Côte-d\'Azur', 'cote d azur')
        ]

        for inp, out in tests:
            self.assertEqual(out, Pattern.normalize(inp, extra=True))


class TestLexer(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        sys.setrecursionlimit(250)
        self.abbreviate = Abbreviate.from_files('LTWA_20170914-modified.csv', 'stopwords.txt')

    def test_lexer(self):
        with open('tests/tests.csv') as f:
            for l in f.readlines():
                fields = l.split('\t')
                self.assertEqual(fields[1].strip(), self.abbreviate(fields[0].strip(), remove_part=True))
