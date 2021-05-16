import sys
from pyiso4.ltwa import Abbreviate

if len(sys.argv) != 2:
    raise Exception('one argument expected')

abbrv = Abbreviate.from_files('LTWA_20170914-modified.csv', 'stopwords.txt')

# print(abbrv._potential_matches('Militært'))

print(abbrv(sys.argv[1]))