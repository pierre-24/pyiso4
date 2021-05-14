from typing import List
from unicodedata import normalize
from unidecode import unidecode
import re

from pyiso4.prefix_tree import PrefixTree
from pyiso4 import lexer as lx


# some useful regex
BOUNDARY = re.compile(r'[-\s\u2013\u2014_.,:;!|=+*\\/"()&#%@$?]')


class Pattern:
    def __init__(self, pattern: str, replacement: str, langs: List[str] = ['mul']):
        self.pattern = pattern
        self.replacement = replacement
        self.langs = langs

        self.start_with_dash = pattern[0] == '-'
        self.end_with_dash = pattern[-1] == '-'

    @classmethod
    def from_line(cls, line: str):
        """Constructed from a LTWA csv line"""

        fields = line.split('\t')
        if len(fields) != 3:
            raise Exception('{} must contain 3 fields'.format(fields))

        pattern = normalize('NFC', fields[0]).lower()
        pattern = re.sub('\\(.*\\)', '', pattern).strip()  # remove annotations

        replacement = fields[1]
        if replacement in ['n.a.', 'n. a.', 'n.a']:
            replacement = '-'

        langs = [lg.strip() for lg in fields[2].split()]

        return cls(pattern, replacement, langs)

    @staticmethod
    def normalize(inp: str, extra: bool = False):
        """Remove diacritics.

        If `extra` is set to true, set all word boundaries to space, and strip string
        """
        # remove the rest of the diacritics
        result = unidecode(inp)

        if extra:
            # normalize strange word boundaries and lower
            result = BOUNDARY.sub(' ', result).lower()
            # remove everything which is not [a-z ]
            result = re.sub(r'[^a-z ]', ' ', result)
            # clean up multi spaces
            result = re.sub(r'\s+', ' ', result).strip()

        return result

    def match(self, word: str, langs: List[str] = None) -> bool:
        """check if word matches the pattern
        """

        # that cannot be!
        if (self.pattern[-1] == '-' and len(self.pattern) > len(word) + 1) or \
                (self.pattern[-1] != '-' and len(self.pattern) > len(word)):
            return False

        # check if similar languages (if provided)
        if langs is not None:
            similar_lang = False
            for language in self.langs:
                if language == 'mul':
                    similar_lang = True
                    break  # works with any language
                if language in langs:
                    similar_lang = True
                    break  # good

            if not similar_lang:
                return False

        pattern = self.pattern
        if self.start_with_dash:
            pattern = str(reversed(pattern))
            word = str(reversed(word))

        for i, c in enumerate(pattern):
            if c == '-':  # ok, good
                return True
            elif c != word[i].lower():
                return False

        return True

    def __repr__(self):
        return 'Pattern({}, {})'.format(self.pattern, self.replacement)


class Abbreviate:
    def __init__(self, ltwa_prefix: PrefixTree, ltwa_suffix: PrefixTree, stopwords: List[str]):
        self.ltwa_prefix = ltwa_prefix
        self.ltwa_suffix = ltwa_suffix

        self.stopwords = stopwords

    @classmethod
    def from_files(cls, ltwa_file: str, stopwords: str):
        """Create an object from the LTWA CSV file and a newline-separated list of stopwords"""

        ltwa_prefix = PrefixTree()
        ltwa_suffix = PrefixTree()

        # get LTWA
        with open(ltwa_file) as f:
            first_line = True
            for line in f.readlines():
                if first_line:
                    first_line = False
                    continue
                if line == '\n':
                    continue
                pattern = Pattern.from_line(line)
                key = Pattern.normalize(pattern.pattern, True)
                if pattern.start_with_dash:
                    ltwa_suffix.insert(str(reversed(key)), pattern)
                else:
                    ltwa_prefix.insert(key, pattern)

        # get stopwords
        with open(stopwords) as f:
            stopwds = [w.strip() for w in f.readlines()]

        return cls(ltwa_prefix, ltwa_suffix, stopwds)

    def _potential_matches(self, word: str, langs: List[str] = None) -> List[Pattern]:
        # normalize
        n_word = Pattern.normalize(word, True)

        # look into prefix
        results = self.ltwa_prefix.search(n_word)

        # look into suffixes
        results += self.ltwa_suffix.search(str(reversed(n_word)))

        # remove everything that does not match
        results = filter(lambda p: p.match(word, langs), results)

        # return longer matches first, with starting dashes if possible
        return sorted(results, key=lambda p: (100 if p.end_with_dash else 0) + len(p.pattern), reverse=True)

    @staticmethod
    def match_capitalization(abbrv: str, original: str) -> str:
        """Matches the capitalization of the `original` word, as long as they are similar
        """

        abbrv = list(abbrv)
        for i, c in enumerate(abbrv):
            if c in [original[i].lower(), original.upper()]:
                abbrv[i] = original[i]

        return ''.join(abbrv)

    def __call__(self, title: str, remove_part: bool = False, langs: List[str] = None) -> str:
        """Abbreviate a title according to the rules of Section 7 in the ISSN manual
        (https://www.issn.org/understanding-the-issn/assignment-rules/issn-manual/)

        TODO:
        - Section 7.1.2 (one word + qualifying information)
        - Section 7.1.3 (one word + supplement)
        - Section 7.1.7 (keep prepositions in expressions like "in vivo" and
          keep place/personal name intact, such as "Los Alamos")
        - Section 7.1.11 is unclear on whether PART should be kept or not
        """

        result = ''
        is_first = True

        lexer = lx.Lexer(title, self.stopwords)
        tokens = []
        prev_article = None

        # filter tokens
        for token in lexer.tokenize():
            # Remove all articles, as per Section 7.1.7
            if token.type == lx.ARTICLE:
                prev_article = token
                continue
            # Remove stopwords, except if it is first, as per Section 7.1.7
            elif token.type == lx.STOPWORD and not is_first:
                continue

            elif token.type == lx.SYMBOLS:
                # Omit comma, replace point by comma, as per Section 7.1.6 (also remove ellipsis)
                token.value = token.value.replace(',', '').replace('.', ',').replace(',,,', '')

                # remove & and + when they are used as "and", as per Section 7.1.10
                if token.value == '&':
                    continue

            # remove part, as suggested per Section 7.1.11 (but keep that optional, since the rule is unclear)
            elif token.type == lx.ORDINAL and tokens[-1].type == lx.PART and remove_part:
                tokens = tokens[:-1]

            # add previous article if followed by a symbol or nothing (was actually an lx.ORDINAL!)
            if prev_article is not None:
                if token.type in [lx.SYMBOLS, lx.EOS]:
                    tokens.append(prev_article)
                prev_article = None

            # keep the token only it contains something
            if token.type != lx.EOS and token.value != '':
                tokens.append(token)

            is_first = False

        # do not abbreviate title which consists of one word (as per Section 7.1.1)
        if len(tokens) == 1:
            result = tokens[0].value
        # when the title is one word with an initial preposition, it is not abbreviated (as per Section 7.1.1)
        elif len(tokens) == 2 and tokens[0].type == lx.STOPWORD:
            result = '{} {}'.format(tokens[0].value, tokens[1].value)
        # when the title is one word and a final symbol, it is not abbreviated (as per Section 7.1.1?)
        elif len(tokens) == 2 and tokens[1].type == lx.SYMBOLS:
            result = '{}{}'.format(tokens[0].value, tokens[1].value)
        # otherwise, abbreviate WORD and PART according to LTWA
        else:
            is_first = True
            for token in tokens:
                abbrv = token.value
                if token.type in [lx.WORD, lx.PART]:
                    patterns = self._potential_matches(abbrv, langs)
                    if len(patterns) > 0:
                        pattern = patterns[0]
                        if pattern.replacement != '-':
                            abbrv = Abbreviate.match_capitalization(pattern.replacement, token.value)
                result += '{}{}'.format(' ' if not is_first else '', abbrv)
                is_first = False

        return result
