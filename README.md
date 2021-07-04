# `pyiso4`

An attempt to implement the [ISO 4](https://en.wikipedia.org/wiki/ISO_4) standard for journal titles abbreviations in Python,
as described in Section 7.1 of the [ISSN Manual](https://www.issn.org/understanding-the-issn/assignment-rules/issn-manual/).
Inspired by [abbrevIso](https://github.com/marcinwrochna/abbrevIso) by @marcinwrochna.


## Install and use

```bash
pip install --upgrade git+https://github.com/pierre-24/pyiso4.git
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

By default, the program abbreviate using [this list of abbreviation](LTWA_20170914-modified.csv) (slightly modified version of LTWA 2017)
and [this list of stopwords](stopwords.txt).
You can change that using ``--ltwa`` and ``--stopwords`` to provide your own files (with the same syntax).

As for rule 7.1.11, namely that abbreviations of generic words such as part, etc. are omitted unless they are required,
the program removes them by default.
To change this behavior, use `--keep-part`.

## Known issues

A list of failed tests is found [here](tests/failed_tests.csv).
It currently fails

+ to fulfil rule 7.1.7 of the manual: keep prepositions in expressions (like ``in vivo``) and place/personal name intact,
+ to fulfil rules 7.1.2, 7.1.3 and 7.1.8 of the same manual (but this is of lesser importance),
+ on compound words (such as ``microengineering``), except if explicitly found in the LTWA,
+ on some [ligatures](https://en.wikipedia.org/wiki/Ligature_(writing)#Ligatures_in_Unicode_(Latin_alphabets)) (handle the common `œ` and `æ`)

## Contributions

Contributions, either with [issues](https://github.com/pierre-24/pyiso4/issues) or [pull requests](https://github.com/pierre-24/pyiso4/pulls) are welcomed.

If you can to contribute, this is the usual deal: 
start by [forking](https://guides.github.com/activities/forking/), then clone your fork

```bash
git clone (...)
cd pyiso4
```

Then setup... And you are good to go :)

```bash
python -m venv venv # a virtualenv is always a good idea
source venv/bin/activate
make install  # install what's needed for dev
```

Don't forget to work on a separate branch, and to run the linting and tests:

```bash
make lint  # flake8
make test  # unit tests
```