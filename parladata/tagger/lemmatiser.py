import _pickle as pickle
import pycrfsuite

from tagger.train_lemmatiser import extract_features_lemma
from tagger.train_tagger import extract_features_msd

# from train_lemmatiser import extract_features_lemma
# from train_tagger import extract_features_msd


class Lemmatiser:
    """
    Wraper class for the tagger
    Use tag_and_lemmatise_tokens()
    """

    trie = pickle.load(open("tagger/sl.marisa", "rb"), encoding="bytes")
    tagger = pycrfsuite.Tagger()
    tagger.open("tagger/sl.msd.model")
    lemmatiser = {
        "model": pickle.load(open("tagger/sl.lexicon.guesser", "rb"), encoding="bytes"),
        "lexicon": pickle.load(open("tagger/sl.lexicon", "rb"), encoding="bytes"),
    }

    def __init__(self):
        # print('Tagger initialised.')
        pass

    def tag_sent(self, sent):
        return self.tagger.tag(extract_features_msd(sent, self.trie))

    def tag_lemmatise_sent(self, sent):
        return [(a, self.get_lemma(b, a)) for a, b in zip(self.tag_sent(sent), sent)]

    def get_lemma(self, token, msd):
        lexicon = self.lemmatiser["lexicon"]
        key = token.lower() + "_" + msd
        if key in lexicon:
            return lexicon[key][0].decode("utf8")
        if msd[:2] != "Np":
            for i in range(len(msd) - 1):
                for key in lexicon.keys(key[: -(i + 1)]):
                    return lexicon[key][0].decode("utf8")
        return self.guess_lemma(token, msd)

    def guess_lemma(self, token, msd):
        if len(token) < 3:
            return self.apply_rule(token, "(0,'',0,'')", msd)
        model = self.lemmatiser["model"]
        if msd not in model:
            return token
        else:
            lemma = self.apply_rule(
                token, model[msd].predict(extract_features_lemma(token))[0], msd
            )
            if len(lemma) > 0:
                return lemma
            else:
                return token

    def apply_rule(self, token, rule, msd):
        rule = list(eval(rule))
        if msd:
            if msd[:2] == "Np":
                lemma = token
            else:
                lemma = token.lower()
        else:
            lemma = token.lower()
        rule[2] = len(token) - rule[2]
        lemma = rule[1] + lemma[rule[0] : rule[2]] + rule[3]
        return lemma

    def test_me(self):
        t = Tokeniser()
        totag = t.only_tokens(t.tokenise(test_text))
        print(totag)
        tags = self.tag_lemmatise_sent(totag)
        print(tags)

    def test_custom(self, txt):
        t = Tokeniser()
        totag = t.only_tokens(t.tokenise(txt))
        tags = self.tag_lemmatise_sent(totag)

    def tag_and_lemmatise_tokens(self, tokens):
        return self.tag_lemmatise_sent(tokens)

    def lemmatise_token(self, token):
        return self.tag_lemmatise_sent([token])
