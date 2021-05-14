from typing import List, Iterable
from unicodedata import normalize
import re

WORD, ABBREVIATION, STOPWORD, ARTICLE, PART, ORDINAL, SYMBOLS, EOS = \
    'WORD', 'ABBREVIATION', 'STOPWORD', 'ARTICLE', 'PART', 'ORDINAL', 'SYMBOLS', 'EOS'

SPACES = ' ', '\t', '\n'

DOT = '.'

PARTS = ['series', 'serie', 'part', 'section', 'série']
PARTS_ABBRV = ['ser', 'sect', 'sec']

ARTICLES = ['a', 'an', 'the', 'der', 'die', 'das', 'den', 'dem', 'des', 'le', 'la', 'les', 'el', 'il', 'lo', 'los',
            'de', 'het', 'els', 'ses', 'es', 'gli', 'een']

# common abbreviation are only accepted with the correct capitalization
COMMON_ABBRV = ['St', 'Mr', 'Ms', 'Mrs', 'Mx', 'Dr', 'Prof', 'vs']

# single (uppercase) letter, or roman letters
IS_ORDINAL = re.compile(r'[A-Z]|[IVXivx]+')


class Token:
    def __init__(self, typ: str, value: str):
        self.type = typ
        self.value = value

    def __repr__(self) -> str:
        return 'T({},{})'.format(self.type, self.value)


class Lexer:
    def __init__(self, inp, stopwords: List[str]):
        self.input = normalize('NFC', inp)
        self.pos = 0
        self.count = -1
        self.current_word = None
        self.stopwords = stopwords

        self.next()

    def _skip_space(self):
        while self.pos < len(self.input) and self.input[self.pos] in SPACES:
            self.pos += 1

    def next(self) -> None:
        """Get the next word"""

        self._skip_space()
        beg = self.pos
        while self.pos < len(self.input) and self.input[self.pos] not in SPACES:
            self.pos += 1

        if beg != self.pos:
            self.current_word = self.input[beg:self.pos]
        else:
            self.current_word = None

        self.count += 1

    def tokenize(self) -> Iterable[Token]:
        was_part = -2

        while self.current_word is not None:
            word = self.current_word
            lower_word = self.current_word.lower()

            # remove symbols at the end
            end_symbols = ''
            while len(lower_word) > 0 and not lower_word[-1].isalpha():
                end_symbols += lower_word[-1]
                lower_word = lower_word[:-1]
                word = word[:-1]

            # if word ends with quote, put it back (plural possessive in english)
            if len(end_symbols) > 0 and end_symbols[0] == "'":
                word = word + "'"
                lower_word = word + "'"
                end_symbols = end_symbols[1:]

            if len(word) > 0:
                # check if abbreviation
                ends_with_dot = len(end_symbols) > 0 and end_symbols[0] == DOT
                if ends_with_dot and (word in COMMON_ABBRV or word.count(DOT) > 0):
                    end_symbols = end_symbols[1:]
                    yield Token(ABBREVIATION, word + DOT)
                # check if common abbreviation anyway (without dot)
                elif word in COMMON_ABBRV:
                    yield Token(ABBREVIATION, word)
                # check if part ending with dot
                elif ends_with_dot and lower_word in PARTS_ABBRV:
                    end_symbols = end_symbols[1:]
                    yield Token(PART, word + DOT)
                    was_part = self.count
                # check if part (without dot)
                elif lower_word in PARTS:
                    yield Token(PART, word)
                    was_part = self.count
                # check if ordinal (preceded by PART)
                elif IS_ORDINAL.match(word) and self.count == was_part + 1:
                    yield Token(ORDINAL, word)
                # check if article (after ordinal, so "a" is detected as ordinal if preceded by PART)
                elif lower_word in ARTICLES:
                    yield Token(ARTICLE, word)
                # check if French "l'" or "d'"
                elif lower_word[0:2] in ["l'", "d'", 'l’', 'd’']:
                    yield Token(ARTICLE, word[0:2])
                    yield Token(WORD, word[2:])  # the rest is assumed to be a word
                # check if Italian "dell'" or "nell'"
                elif lower_word[0:5] in ["dell'", "nell'", 'dell’', 'nell’']:
                    yield Token(ARTICLE, word[0:5])
                    yield Token(WORD, word[5:])  # the rest is assumed to be a word
                # check if stopword
                elif lower_word in self.stopwords:
                    yield Token(STOPWORD, word)
                # otherwise ...
                else:
                    yield Token(WORD, word)

            # yield the remaining symbols, if any
            if len(end_symbols) > 0:
                yield Token(SYMBOLS, end_symbols)

            self.next()

        yield Token(EOS, '\0')
