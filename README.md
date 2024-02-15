# `pyiso4`

An attempt to implement the [ISO 4](https://en.wikipedia.org/wiki/ISO_4) standard for journal titles abbreviations within a simple application written in Python, as described in Section 7.1 of the [ISSN Manual](https://www.issn.org/understanding-the-issn/assignment-rules/issn-manual/).
Inspired by the NPM package [abbrevIso](https://github.com/marcinwrochna/abbrevIso).


## Install and use

From [PyPI](https://pypi.org/project/pyiso4/):

```bash
pip install pysiso4
```

Usage:

```text
$ iso4abbreviate "Journal of the American Chemical Society"
J. Am. Chem. Soc.
```

You can abbreviate multiple titles at the same time:

```text
$ iso4abbreviate "Journal of Chemical Physics" "Journal of Physical Chemistry A"
J. Chem. Phys.
J. Phys. Chem. A
```

By default, the program abbreviate using [this list of abbreviation](https://github.com/pierre-24/pyiso4/blob/master/pyiso4/LTWA_20210702.csv) (slightly modified version of LTWA 2021)
and [this list of stopwords](https://github.com/pierre-24/pyiso4/blob/master/pyiso4/stopwords.txt).
You can change that using `--ltwa` and `--stopwords` to provide your own files instead (with the same syntax as theirs).

As for rule 7.1.11, namely that abbreviations of generic words such as part, etc. are omitted unless they are required,
the program removes them by default.
To change this behavior, use `--keep-part`.

## Python API

````python
from pyiso4.ltwa import Abbreviate

# create an abbreviator (using the default LTWA)
abbreviator = Abbreviate.create()

# abbreviate something
abbreviation = abbreviator('Journal of the American Chemical Society', remove_part=True)
````

## Known issues

A list of failed tests is found [here](tests/failed_tests.tsv).
It currently fails:

+ to fulfil rule 7.1.7 of the manual: keep prepositions in expressions (like *in vivo*) and place/personal name intact (it is difficult to know in advance),
+ to fulfil rules 7.1.2, 7.1.3 and 7.1.8 of the same manual (but this is of lesser importance),
+ on compound words (such as *microengineering*), except if explicitly found in the LTWA,
+ on some [ligatures](https://en.wikipedia.org/wiki/Ligature_(writing)#Ligatures_in_Unicode_(Latin_alphabets)) (but it handles the most common ones, such as `œ` and `æ`)


## Contributions

Contributions, either by filling [issues](https://github.com/pierre-24/pyiso4/issues) or via [pull requests](https://github.com/pierre-24/pyiso4/pulls) are welcomed.
More information [here](https://github.com/pierre-24/pyiso4/blob/dev/CONTRIBUTING.md).
