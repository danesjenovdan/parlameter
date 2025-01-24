#!/bin/bash

# prepare marisa for tagger training
echo "Preparing marisa for tagger training."
cat sloleks_clarin_2.0-en.ud.tbl | cut -f 1,2,3 | python prepare_marisa.py sl.marisa
echo "Generated the following files: sl.lemma_freq, sl.marisa"


# train the tagger
echo "Training the tagger, this will take 6-ish hours."
python train_tagger.py sl
echo "Generated the following files: sl.msd.model"

# prepare the lexicon for the lemmatizer
echo "Preparing the lexicon for the lemmatizer."
python lemma_freq.py sl.lemma_freq < sl.train
echo "Created the following files: sl.lemma_freq"

# transform the lexicon into a marisa_trie.BytesTrie
echo "Transforming the lexicon into a marise_trie.BytesTrie."
cat sloleks_clarin_2.0-en.ud.tbl | cut -f 1,2,3 | python prepare_lexicon.py sl.lemma_freq sl.lexicon
echo "Created the following files: sl.lexicon, sl.lexicon.train"

# train the lemma guesser
echo "Training lemmatiser."
python train_lemmatiser.py sl.lexicon
echo "Created the following files: sl.lexicon.guesser"
