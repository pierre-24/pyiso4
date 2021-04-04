from pyiso4.ltwa import Abbreviate

abbrv = Abbreviate.from_files('LTWA_20170914.csv', 'stopwords.txt')

print(list(p.pattern for p in abbrv.ltwa_prefix.search('cryptography')))