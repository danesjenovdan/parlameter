from parlacards.lemmatizers.sl.stop_words import STOPWORDS


def get_stopwords():
    return STOPWORDS


def lemmatize_many(speech):
    # initialize the lemmatizer class only once
    from parlacards.lemmatizers.classla import ClasslaLemmatizer
    lemmatiser = ClasslaLemmatizer("sl")
    return " ".join(lemmatiser.lemmatize(speech))
