from datetime import datetime
from itertools import combinations

from django.db.models import Count, Max

from parlacards.models import GroupVotingDistance, VotingDistance
from parlacards.scores.common import get_dates_between, get_fortnights_between
from parladata.models.ballot import Ballot
from parladata.models.common import Mandate
from parladata.models.memberships import PersonMembership
from parladata.models.vote import Vote

# only compare options when there was a vote
options_to_compare = ["for", "against", "abstain"]


#
# PERSON
#
def calculate_voting_distance(from_person, to_person, timestamp=None):
    if not timestamp:
        timestamp = datetime.now()

    mandate = Mandate.get_active_mandate_at(timestamp)

    from_ballots = Ballot.objects.filter(
        personvoter=from_person,
        vote__timestamp__lte=timestamp,
        vote__motion__session__mandate=mandate,
        option__in=options_to_compare,
    )

    to_ballots = Ballot.objects.filter(
        personvoter=to_person,
        vote__timestamp__lte=timestamp,
        vote__motion__session__mandate=mandate,
        option__in=options_to_compare,
    )

    # we will only calculate the distance for voting events
    # where both from_person and to_person participated
    vote_ids_intersection = set(
        from_ballots.values_list("vote_id", flat=True)
    ).intersection(
        set(
            to_ballots.values_list(
                "vote_id",
                flat=True,
            )
        )
    )

    # get ballots where both parties participated
    filtered_from_ballots = from_ballots.filter(
        vote__id__in=vote_ids_intersection
    ).order_by("vote__id")
    filtered_to_ballots = to_ballots.filter(
        vote__id__in=vote_ids_intersection
    ).order_by("vote__id")

    # number of ballots where both parties participated
    ballots_to_compare_count = len(vote_ids_intersection)
    # number of ballots where parties voted the same
    voted_the_same_count = len(
        [
            from_ballot
            for from_ballot, to_ballot in zip(
                filtered_from_ballots.values_list("option", flat=True),
                filtered_to_ballots.values_list("option", flat=True),
            )
            if from_ballot == to_ballot
        ]
    )

    # if there are not ballots to compare
    if ballots_to_compare_count == 0:
        return 0  # TODO: not sure what to do in this case
    else:
        # print(from_person, to_person, voted_the_same_count / ballots_to_compare_count * 100)
        # return match value in percentage
        return voted_the_same_count / ballots_to_compare_count * 100


def save_voting_distance(from_person, to_person, playing_field, timestamp=None):
    if not timestamp:
        timestamp = datetime.now()

    VotingDistance(
        person=from_person,
        target=to_person,
        value=calculate_voting_distance(from_person, to_person, timestamp),
        timestamp=timestamp,
        playing_field=playing_field,
    ).save()


def save_voting_distances(playing_field, timestamp=None):
    if not timestamp:
        timestamp = datetime.now()

    people = playing_field.query_voters(timestamp)
    pairs = combinations(people, 2)

    for pair in pairs:
        distance = calculate_voting_distance(pair[0], pair[1], timestamp)

        VotingDistance(
            person=pair[0],
            target=pair[1],
            value=distance,
            timestamp=timestamp,
            playing_field=playing_field,
        ).save()

        VotingDistance(
            person=pair[1],
            target=pair[0],
            value=distance,
            timestamp=timestamp,
            playing_field=playing_field,
        ).save()


def save_voting_distances_between(playing_field, datetime_from=None, datetime_to=None):
    if not datetime_from:
        datetime_from = datetime.now()
    if not datetime_to:
        datetime_to = datetime.now()

    for day in get_dates_between(datetime_from, datetime_to):
        save_voting_distances(playing_field, timestamp=day)


def save_sparse_voting_distances_between(
    playing_field, datetime_from=None, datetime_to=None
):
    if not datetime_from:
        datetime_from = datetime.now()
    if not datetime_to:
        datetime_to = datetime.now()

    for day in get_fortnights_between(datetime_from, datetime_to):
        save_voting_distances(playing_field, timestamp=day)


#
# GROUP
#


def calculate_group_voting_distance(group, playing_field, timestamp=None):
    if not timestamp:
        timestamp = datetime.now()

    mandate = Mandate.get_active_mandate_at(timestamp)

    # get all votes from this mandate
    votes = Vote.objects.filter(
        timestamp__lte=timestamp, motion__session__mandate=mandate
    )

    # dictionary to contain the output
    # keys are person ids and values are
    # distances to the party
    output = {}

    # dictionary to contain "average" ballots of the party
    # keys are vote ids and values are
    # vote option: for / against / abstain
    party_ballots = {}

    # calculate "average" party ballots
    for vote in votes:
        # get relevant voters
        voters = PersonMembership.valid_at(vote.timestamp).filter(
            on_behalf_of=group, role="voter"
        )

        # if a vote did not have a group participating skip it
        if voters.count() == 0:
            continue

        ballots = Ballot.objects.filter(
            vote=vote,
            personvoter__in=voters.values_list("member_id", flat=True),
            option__in=options_to_compare,
        )

        options_aggregated = (
            ballots.values("option")
            .annotate(dcount=Count("option"))
            .order_by()
            .aggregate(Max("option"))
        )
        # If you don't include the order_by(),
        # you may get incorrect results if the
        # default sorting is not what you expect.

        # if no option was in majority, skip this vote
        if not options_aggregated["option__max"]:
            continue

        # add to ballots dictionary
        party_ballots[vote.id] = options_aggregated["option__max"]

    # get all voters
    relevant_voters = playing_field.query_voters(timestamp)

    for person in relevant_voters:
        # get personal ballots and exclude the ones
        # that were problematic on the party level

        sorted_person_ballots = Ballot.objects.filter(
            personvoter=person,
            option__in=options_to_compare,
            vote__id__in=party_ballots.keys(),
        )

        # number of ballots where both group and voter participated
        ballots_to_compare_count = len(sorted_person_ballots)
        # number of ballots where group and voter voted the same
        voted_the_same_count = len(
            [b for b in sorted_person_ballots if b.option == party_ballots[b.vote.id]]
        )

        # if there are not ballots to compare
        if ballots_to_compare_count == 0:
            continue  # TODO: what to do in this case?
        else:
            # save match value in percentage to output dictionary
            # print(group, person, voted_the_same_count / ballots_to_compare_count * 100)
            output[person.id] = voted_the_same_count / ballots_to_compare_count * 100

    return output


def save_group_voting_distance(group, playing_field, timestamp=None):
    if not timestamp:
        timestamp = datetime.now()

    distances = calculate_group_voting_distance(group, playing_field)

    for person_id in distances.keys():
        GroupVotingDistance(
            group=group,
            target_id=person_id,
            value=distances[person_id],
            timestamp=timestamp,
            playing_field=playing_field,
        ).save()


def save_groups_voting_distances(playing_field, timestamp=None):
    if not timestamp:
        timestamp = datetime.now()

    groups = playing_field.query_parliamentary_groups(timestamp)
    for group in groups:
        save_group_voting_distance(group, playing_field, timestamp)


def save_groups_voting_distances_between(
    playing_field, datetime_from=None, datetime_to=None
):
    if not datetime_from:
        datetime_from = datetime.now()
    if not datetime_to:
        datetime_to = datetime.now()

    for day in get_dates_between(datetime_from, datetime_to):
        save_groups_voting_distances(playing_field, timestamp=day)


def save_sparse_groups_voting_distances_between(
    playing_field, datetime_from=None, datetime_to=None
):
    if not datetime_from:
        datetime_from = datetime.now()
    if not datetime_to:
        datetime_to = datetime.now()

    for day in get_fortnights_between(datetime_from, datetime_to):
        save_groups_voting_distances(playing_field, timestamp=day)


# TODO this is not used, but still interesting
# leaving it here in case we persuade product people this is interesting
def assign_value_to_option_string(option_string):
    return {
        "for": 1,
        "against": -1,
        "abstain": 0,
        "absent": 0,
        "did not vote": 0,
    }[option_string]


# implement this with numpy
# IF AND ONLY IF we need
# numpy someplace else
def euclidean(v1, v2):
    return sum((p - q) ** 2 for p, q in zip(v1, v2)) ** 0.5


def calculate_voting_distance_between_groups(from_group, to_group, timestamp=None):
    if not timestamp:
        timestamp = datetime.now()

    mandate = Mandate.get_active_mandate_at(timestamp)

    # get all relevant votes
    votes = Vote.objects.filter(
        timestamp__lte=timestamp, motion__session__mandate=mandate
    ).order_by("-timestamp")

    from_party_ballots = []
    to_party_ballots = []

    for vote in votes:
        # get relevant voters
        from_voters = PersonMembership.valid_at(vote.timestamp).filter(
            on_behalf_of=from_group, role="voter"
        )
        to_voters = PersonMembership.valid_at(vote.timestamp).filter(
            on_behalf_of=to_group, role="voter"
        )

        # if a vote did not have a group participating continue
        if (from_voters.count() == 0) or (to_voters.count() == 0):
            continue

        from_ballots = Ballot.objects.filter(
            vote=vote, personvoter__in=from_voters.values_list("member_id", flat=True)
        ).exclude(
            # TODO Filip would remove this
            # because when everyone is absent
            # this voting event will not have
            # a max option but this needs
            # consultation with product people
            option="absent"
        )

        to_ballots = Ballot.objects.filter(
            vote=vote, personvoter__in=to_voters.values_list("member_id", flat=True)
        ).exclude(
            # TODO Filip would remove this
            # because when everyone is absent
            # this voting event will not have
            # a max option but this needs
            # consultation with product people
            option="absent"
        )

        from_options_aggregated = (
            from_ballots.values("option")
            .annotate(dcount=Count("option"))
            .order_by()
            .aggregate(Max("option"))
        )
        # If you don't include the order_by(),
        # you may get incorrect results if the
        # default sorting is not what you expect.

        to_options_aggregated = (
            to_ballots.values("option")
            .annotate(dcount=Count("option"))
            .order_by()
            .aggregate(Max("option"))
        )
        # If you don't include the order_by(),
        # you may get incorrect results if the
        # default sorting is not what you expect.

        if not (
            from_options_aggregated["option__max"]
            and to_options_aggregated["option__max"]
        ):
            continue

        from_party_ballots.append(from_options_aggregated["option__max"])
        to_party_ballots.append(to_options_aggregated["option__max"])

    from_coordinates = [
        assign_value_to_option_string(option_string)
        for option_string in from_party_ballots
    ]
    to_coordinates = [
        assign_value_to_option_string(option_string)
        for option_string in to_party_ballots
    ]

    return euclidean(from_coordinates, to_coordinates)


def save_voting_distance_between_groups(playing_field, timestamp=None):
    if not timestamp:
        timestamp = datetime.now()

    groups = playing_field.query_parliamentary_groups(timestamp)
    pairs = combinations(groups, 2)

    for pair in pairs:
        distance = calculate_group_voting_distance(pair[0], pair[1], timestamp)

        GroupVotingDistance(
            group=pair[0],
            target=pair[1],
            value=distance,
            timestamp=timestamp,
            playing_field=playing_field,
        ).save()

        GroupVotingDistance(
            group=pair[1],
            target=pair[0],
            value=distance,
            timestamp=timestamp,
            playing_field=playing_field,
        ).save()
