from typing import List, Tuple
from unidecode import unidecode
import re
import pathlib

from pyiso4.prefix_tree import PrefixTree
from pyiso4.lexer import Lexer, TokenType
from pyiso4.normalize_string import normalize, Level, BOUNDARY, number_of_ligatures


class Pattern:
    INFLECTION = re.compile(r'^([iaesn\'’]{1,3})')

    def __init__(self, pattern: str, replacement: str, langs: List[str] = ['mul']):
        self.pattern = pattern
        self.replacement = replacement
        self.langs = langs

        self.start_with_dash = pattern[0] == '-'
        self.end_with_dash = pattern[-1] == '-'

    @staticmethod
    def normalize(inp: str) -> str:
        """Normalization for the patterns (and keys): unidecode + lowering
        """

        return normalize(inp, Level.NORMAL).lower()

    @classmethod
    def from_line(cls, line: str):
        """Constructed from a LTWA csv line"""

        fields = line.split('\t')
        if len(fields) != 3:
            raise Exception('{} must contain 3 fields'.format(fields))

        pattern = re.sub('\\(.*\\)', '', fields[0]).strip()  # remove annotations
        pattern = Pattern.normalize(pattern)

        replacement = fields[1]
        if replacement in ['n.a.', 'n. a.', 'n.a']:
            replacement = '-'

        langs = [lg.strip() for lg in fields[2].split()]

        return cls(pattern, replacement, langs)

    def to_key(self) -> str:
        """Get the key for the tree, without start or end dash"""

        if self.start_with_dash:
            return self.pattern[1:]
        elif self.end_with_dash:
            return self.pattern[:-1]
        else:
            return self.pattern

    def match(self, sentence: str, langs: List[str] = None) -> bool:
        """Check if the pattern matches the begining of ``sentence``.
        Assume that it has been normalized.
        """

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

        # if there is a starting or ending dash, the pattern cannot be larger than the word
        if self.start_with_dash or self.end_with_dash:
            if len(self.pattern) > (len(sentence) + 1):
                return False
        # if there is no dash, the lengths should be, at most, the same
        else:
            if len(self.pattern) > len(sentence):
                return False

        pattern = self.pattern
        if self.start_with_dash:
            pattern = str(reversed(pattern))
            sentence = str(reversed(sentence))

        final_pos = 0
        for i, c in enumerate(pattern):
            final_pos = i
            if c == '-' and i == len(pattern) - 1:  # ok, good
                return True
            elif c != sentence[i].lower():
                return False

        # now, does this ends well?
        inflection = Pattern.INFLECTION.match(sentence[final_pos + 1:])
        if inflection is not None:
            final_pos += inflection.span()[1]

        if final_pos == len(sentence) - 1:  # nothing else, so that's a match
            return True
        else:  # if that's a boundary, then its a match
            return BOUNDARY.match(sentence[final_pos + 1:]) is not None

    def __repr__(self):
        return 'Pattern({}, {})'.format(self.pattern, self.replacement)


_here = pathlib.Path(__file__).parent


class Abbreviate:
    def __init__(self, ltwa_prefix: PrefixTree, ltwa_suffix: PrefixTree, stopwords: List[str]):
        self.ltwa_prefix = ltwa_prefix
        self.ltwa_suffix = ltwa_suffix

        self.stopwords = stopwords

    @classmethod
    def create(
            cls,
            ltwa_file: str = _here / 'LTWA_20170914-modified.csv',
            stopwords: str = _here / 'stopwords.txt'):
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
                key = pattern.to_key()
                if pattern.start_with_dash:
                    ltwa_suffix.insert(key[::-1], pattern)
                else:
                    ltwa_prefix.insert(key, pattern)

        # get stopwords
        stopwds = []
        if stopwords is not None:
            with open(stopwords) as f:
                stopwds = [w.strip() for w in f.readlines()]

        return cls(ltwa_prefix, ltwa_suffix, stopwds)

    def _potential_matches(self, sentence: str, langs: List[str] = None) -> List[Pattern]:
        # look into prefix
        results = self.ltwa_prefix.search(sentence)

        # look into suffixes
        results += self.ltwa_suffix.search(str(reversed(sentence)))

        # remove everything that does not match
        results = filter(lambda p: p.match(sentence, langs), results)

        # return longer matches first, with ending dashes if possible
        return sorted(
            results,
            key=lambda p: (100 if p.end_with_dash else 0) + len(p.pattern),
            reverse=True)

    @staticmethod
    def match_capitalization_and_diacritic(abbrv: str, original: str) -> str:
        """Matches the capitalization and diacritics of the `original` word, as long as they are similar
        """

        abbrv = list(normalize(abbrv, Level.SOFT))
        for i, c in enumerate(abbrv):
            unided = unidecode(original[i])
            if unidecode(c) in [unided.lower(), unided.upper()]:
                abbrv[i] = original[i]

        return ''.join(abbrv)

    def abbreviate(self, sentence: str, fallback: str, guide: str, langs: List[str] = None) -> Tuple[str, int]:
        """Abbreviate the beginning of ``sentence`` by looking for an appropriate pattern.
        If not found, use ``fallback``. If found, matches the capitalization given by ``guide``.
        Also returns the length of the sentence that was replaced.
        """

        patterns = self._potential_matches(sentence, langs)
        if len(patterns) > 0:
            pattern = patterns[0]
            if pattern.replacement != '-':
                return Abbreviate.match_capitalization_and_diacritic(pattern.replacement, guide), len(pattern.pattern)
            else:
                return fallback, len(fallback)

        return fallback, len(fallback)

    def __call__(self, title: str, remove_part: bool = True, langs: List[str] = None) -> str:
        """Abbreviate a title according to the rules of Section 7 in the ISSN manual
        (https://www.issn.org/understanding-the-issn/assignment-rules/issn-manual/)

        TODO:
        - Section 7.1.2 (one word + qualifying information)
        - Section 7.1.3 (one word + supplement)
        - Section 7.1.7 (keep prepositions in expressions like "in vivo" and
          keep place/personal name intact, such as "Los Alamos")
        - Section 7.1.8 (acronyms and initialism)
        - Section 7.1.11 is unclear on whether PART should be kept or not
        """

        result = ''
        is_first = True

        title_soft_normalized = normalize(title, Level.SOFT)
        title_normalized = Pattern.normalize(title)

        lexer = Lexer(title_soft_normalized, self.stopwords)
        tokens = []
        prev_article = None

        # filter tokens
        for token in lexer.tokenize():
            # Remove all articles, as per Section 7.1.7
            if token.type == TokenType.ARTICLE:
                prev_article = token
                continue
            # Remove stopwords, except if it is first, as per Section 7.1.7
            elif token.type == TokenType.STOPWORD and not is_first:
                continue

            elif token.type == TokenType.SYMBOLS:
                # Omit comma, replace point by comma, as per Section 7.1.6 (also remove ellipsis)
                token.value = token.value.replace(',', '').replace('.', ',').replace(',,,', '')

                # remove & and + when they are used as "and", as per Section 7.1.10
                if token.value == '&':
                    continue

            # remove part, as suggested per Section 7.1.11 (but keep that optional, since the rule is unclear)
            elif token.type == TokenType.ORDINAL and tokens[-1].type == TokenType.PART and remove_part:
                tokens = tokens[:-1]

            # add previous article if followed by a symbol or nothing (was actually an ORDINAL!)
            if prev_article is not None:
                if token.type in [TokenType.SYMBOLS, TokenType.EOS]:
                    tokens.append(prev_article)
                prev_article = None

            # keep the token only it contains something
            if token.type != TokenType.EOS and token.value != '':
                tokens.append(token)

            is_first = False

        # do not abbreviate title which consists of one word (as per Section 7.1.1)
        if len(tokens) == 1:
            result = tokens[0].value
        # when the title is one word with an initial preposition, it is not abbreviated (as per Section 7.1.1)
        elif len(tokens) == 2 and tokens[0].type == TokenType.STOPWORD:
            result = '{} {}'.format(tokens[0].value, tokens[1].value)
        # when the title is one word and a final symbol, it is not abbreviated (as per Section 7.1.1?)
        elif len(tokens) == 2 and tokens[1].type == TokenType.SYMBOLS:
            result = '{}{}'.format(tokens[0].value, tokens[1].value)
        # otherwise, abbreviate WORD and PART according to LTWA
        else:
            is_hyphenated = False
            no_space = False
            next_position = 0
            ligatures_shift = 0

            for token in tokens:
                abbrv = token.value

                if token.type == TokenType.HYPHEN:
                    is_hyphenated = True
                elif token.type in [TokenType.WORD, TokenType.PART]:
                    if token.position >= next_position:
                        abbrv, len_ = self.abbreviate(
                            title_normalized[token.position + ligatures_shift:],
                            token.value,
                            title_soft_normalized[token.position:],
                            langs)
                        next_position = token.position + len_
                    else:
                        abbrv = ''
                        no_space = True
                elif token.type in [TokenType.SYMBOLS, TokenType.HYPHEN]:
                    no_space = True

                result += '{}{}'.format(
                    ' ' if not (len(result) == 0 or is_hyphenated or no_space)
                    else '',
                    abbrv)

                ligatures_shift += number_of_ligatures(token.value)
                no_space = False
                if token.type != TokenType.HYPHEN:
                    is_hyphenated = False

        return result
