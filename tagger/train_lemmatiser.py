#!/usr/bin/python
# -*-coding:utf8-*-
import sys

import _pickle as pickle
from sklearn.feature_extraction import DictVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeClassifier


def suffix(token, n):
    if len(token) > n:
        return token[-n:]


def extract_features_lemma(token):
    features = {}
    for i in range(4):
        suf = suffix(token, i + 1)
        if suf != None:
            features["suf" + str(i + 1)] = suf
    if len(token) > 3:
        features["pref3"] = token[:3]
    #   print(features)
    return features


if __name__ == "__main__":
    lexicon = pickle.load(open(sys.argv[1] + ".train", "rb"))

    train = {}
    for token, msd, label in lexicon:
        # print(token, msd, label)
        if msd not in train.keys():
            train[msd] = set()
        train[msd].add((token, label))
    print(len(list(train.keys())))

    models = {}
    for i, msd in enumerate(train.keys()):
        # print(i, msd)
        if msd[0] not in "NAVRM" or msd[:2] == "Va":
            continue
        x = []
        y = []
        for token, label in train[msd]:
            x.append(extract_features_lemma(token))
            y.append(label)
        p = Pipeline([("vect", DictVectorizer()), ("clf", MultinomialNB())])
        p.fit(x, y)
        # print p.predict(extract_features(u'kolege'))
        # break
        # print(i, msd)
        models[msd] = p

    pickle.dump(models, open(sys.argv[1] + ".guesser", "wb"), 1)
