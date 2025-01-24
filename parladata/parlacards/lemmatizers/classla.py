try:
    import classla
except ModuleNotFoundError:
    raise ModuleNotFoundError(
        "You need to install the classla library. Run 'pip install git+https://github.com/danesjenovdan/classla.git@upgrade-numpy'."
    )


class ClasslaLemmatizer:
    nlp = None

    def __init__(self, language_code):
        if not ClasslaLemmatizer.nlp:
            classla.download(language_code)
            ClasslaLemmatizer.nlp = classla.Pipeline(
                language_code, processors="tokenize,pos,lemma"
            )

    def lemmatize(self, text):
        doc = self.nlp(text)
        return [word.lemma for word in doc.iter_words() if word.upos != "PUNCT"]
