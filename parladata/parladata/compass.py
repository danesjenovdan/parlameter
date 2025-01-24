# -*- coding: utf-8 -*-
from parladata.models import *


def removekey(d, key):
    r = dict(d)
    del r[key]
    return r


def getVotingArray():
    persons = Person.objects.all()
    votes = Vote.objects.all()

    results = {}

    # for each person
    for i, person in enumerate(persons):

        # generate new line
        # results.append([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]) # 100 zeroes

        # generate voting record
        record = []

        print("Processing votes for " + person.name)

        # for each vote that happened
        for vote in votes:

            # check if person voted
            if len(vote.ballots.filter(voter=person)) != 0:
                record.append(vote.ballots.filter(voter=person)[0].option)
            else:
                record.append(0)

        results[person.name] = record

        # compare with all other people
    #            otherpersons = list(persons)
    #            otherpersons.remove(person)
    #            for k, other in enumerate(otherpersons):
    #                if ballot.option == other.ballots.all().order_by('vote')[j].option:
    #                    results[i][k] = results[i][k] + 1

    print("Finished processing votes.")

    return results


def getScores(results):

    scores = {}

    # for all people
    for i, person in enumerate(results):

        print("Processing person " + person)

        # make new person score
        scores[person] = []

        # for every other person
        # otherpeople = removekey(results, person)

        for other in results:

            print("Other " + other)

            score = 0
            # for every vote
            for j, vote in enumerate(results[person]):

                # print 'Vote ' + str(j)

                # if vote is the same
                if results[other][j] == vote:
                    # add to score
                    score = score + 1

            # when done comparing votes, add score to person
            scores[person].append(score)

    return scores


def getAll():

    return getScores(getVotingArray())
