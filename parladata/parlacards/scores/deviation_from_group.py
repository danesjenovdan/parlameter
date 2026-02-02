from datetime import datetime

from django.db.models import Count, Max, Q

from parlacards.models import DeviationFromGroup
from parlacards.scores.common import get_dates_between, get_fortnights_between
from parladata.models.ballot import Ballot
from parladata.models.common import Mandate
from parladata.models.memberships import PersonMembership


def deviation_percentage_between_two_lists(list1, list2):
    if len(list1) != len(list2):
        raise ValueError(
            "In order to calculate deviation percentage, the lists need to be the same lenght."
        )

    if len(list1) == 0:
        return 0

    mismatches = 0
    for i, item in enumerate(list1):
        if item != list2[i]:
            mismatches += 1

    return mismatches / len(list1) * 100


def get_group_ballot(vote, people_ids, exclude_absent=False):
    # vote can be a Vote object
    # or an int representing the object id
    ballots = Ballot.objects.filter(vote=vote, personvoter__id__in=people_ids)

    if exclude_absent:
        ballots.exclude(option="absent")

    options_aggregated = (
        ballots.values("option")
        .annotate(dcount=Count("option"))
        .order_by()
        .aggregate(Max("option"))
    )
    # If you don't include the order_by(),
    # you may get incorrect results if the
    # default sorting is not what you expect.
    return options_aggregated["option__max"]


def calculate_deviation_from_group(
    person, playing_field, timestamp=None, exclude_absent=False
):
    if not timestamp:
        timestamp = datetime.now()

    mandate = Mandate.get_active_mandate_at(timestamp)

    personal_ballots = Ballot.objects.filter(
        personvoter=person,
        vote__timestamp__lte=timestamp,
        vote__motion__session__mandate=mandate,
    ).order_by("vote__id")

    if exclude_absent:
        personal_ballots.exclude(option="absent")

    # only compare people on the votes the person
    # had a chance to vote on
    relevant_vote_ids = personal_ballots.order_by("vote__id").values_list(
        "vote__id", flat=True
    )

    # TODO check this
    voter_membership = PersonMembership.objects.filter(
        Q(start_time__lte=timestamp) | Q(start_time__isnull=True),
        Q(end_time__gte=timestamp) | Q(end_time__isnull=True),
        Q(member=person),
        Q(organization=playing_field),
        Q(role="voter"),
    ).first()
    # parliamentary_group = person.parliamentary_group_on_date(timestamp)
    if not voter_membership:
        raise ValueError(
            f"{person} has no voter membership in {playing_field} at {timestamp}"
        )
        # relevant_people = Person.objects.none()

    parliamentary_group = voter_membership.on_behalf_of

    if not parliamentary_group:
        # voter membership without on_behalf_of means that this is unaffiliated member
        return None

    relevant_people_ids = PersonMembership.objects.filter(
        Q(start_time__lte=timestamp) | Q(start_time__isnull=True),
        Q(end_time__gte=timestamp) | Q(end_time__isnull=True),
        Q(organization=playing_field),
        Q(on_behalf_of=parliamentary_group),
        Q(role="voter"),
    ).values_list("member__id")

    personal_options = [
        option_string
        for option_string in personal_ballots.values_list("option", flat=True)
    ]
    group_options = [
        get_group_ballot(vote_id, relevant_people_ids) for vote_id in relevant_vote_ids
    ]

    return deviation_percentage_between_two_lists(personal_options, group_options)


def save_deviation_from_group(person, playing_field, timestamp=None):
    if not timestamp:
        timestamp = datetime.now()

    DeviationFromGroup(
        person=person,
        playing_field=playing_field,
        timestamp=timestamp,
        value=calculate_deviation_from_group(person, playing_field, timestamp),
    ).save()


def save_people_deviations_from_group(playing_field, timestamp=None):
    if not timestamp:
        timestamp = datetime.now()

    people = playing_field.query_voters(timestamp)

    for person in people:
        try:
            save_deviation_from_group(person, playing_field, timestamp)
        except ValueError as e:
            # TODO log this?
            print("ERROR", e)


def save_people_deviations_from_group_between(
    playing_field, datetime_from=None, datetime_to=None
):
    if not datetime_from:
        datetime_from = datetime.now()
    if not datetime_to:
        datetime_to = datetime.now()

    for day in get_dates_between(datetime_from, datetime_to):
        save_people_deviations_from_group(playing_field, timestamp=day)


def save_sparse_people_deviations_from_group_between(
    playing_field, datetime_from=None, datetime_to=None
):
    if not datetime_from:
        datetime_from = datetime.now()
    if not datetime_to:
        datetime_to = datetime.now()

    for day in get_fortnights_between(datetime_from, datetime_to):
        save_people_deviations_from_group(playing_field, timestamp=day)
