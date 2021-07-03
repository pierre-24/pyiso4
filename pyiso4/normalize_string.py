from enum import Enum, unique
import re
from unicodedata import normalize as unicode_normalize
from unidecode import unidecode


BOUNDARY = re.compile(r'[-\s\u2013\u2014_.,:;!|=+*\\/"()&#%@$?]')


@unique
class Level(Enum):
    SOFT = 1
    NORMAL = 2
    HARD = 3


def normalize(inp: str, level: Level = Level.SOFT) -> str:
    """Normalize the string

    + If ``Level.SOFT``, only ``NFKC`` the string (combination, compatibility equivalence)
    + If ``Level.NORMAL``, all diacritics are transformed, thanks to ``unidecode``
    + If ``Level.HARD``, on top of the previous one, ensure that the result is in ``[a-z ]`` by
      lowering the string and transforming all ``BOUNDARY`` to simple spaces

    """
    if level == Level.SOFT:
        return unicode_normalize('NFKC', inp)
    else:
        result = unidecode(inp)
        if level == Level.HARD:
            result = BOUNDARY.sub(' ', result).lower()  # transform boundaries and lower
            result = re.sub(r'[^a-z ]', ' ', result)  # remove everything which is not [a-z ]

        return result
