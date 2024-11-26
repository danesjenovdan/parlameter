from uk_stemmer import UkStemmer
from parlacards.scores.common import tokenize, remove_punctuation

from parlacards.lemmatizers.ua.stop_words import STOPWORDS


def get_stopwords():
    return STOPWORDS


# initialize the stemmer class only once
stemmer = UkStemmer()


def lemmatize(token):
    return stemmer.stem_word(token)


def lemmatize_many(speech):
    return " ".join(
        [
            stemmer.stem_word(token)
            for token in tokenize(remove_punctuation(speech.strip()))
        ]
    )
