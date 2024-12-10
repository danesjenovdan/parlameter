from parlacards.lemmatizers.sl.stop_words import STOPWORDS


def get_stopwords():
    return STOPWORDS


def lemmatize_many(speech):
    from parlacards.lemmatizers.classla import ClasslaLemmatizer

    # initialize the lemmatizer class only once
    lemmatiser = ClasslaLemmatizer("hr")
    return " ".join(lemmatiser.lemmatize(speech))
