#!/usr/bin/python
import sys

import _pickle as pickle

lemma_freq = {}
for line in sys.stdin:
    try:
        # print(line.split('\t')[0])
        # lemma=line.decode('utf8').split('\t')
        # print(lemma)
        # lemma=lemma[2].lower()+'_'+lemma[4][:2]
        lemma = line.split("\t")
        lemma = lemma[1].lower() + "_" + lemma[2][:2]
    except:
        continue
    lemma_freq[lemma] = lemma_freq.get(lemma, 0) + 1
print(list(lemma_freq)[:10])
pickle.dump(lemma_freq, open(sys.argv[1], "wb"), 1)  # sl.lemma_freq
