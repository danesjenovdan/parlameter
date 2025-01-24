from datetime import datetime, timedelta

from django.db.models import Count, Q
from django.db.models.functions import TruncMonth

from parlacards.models import GroupMonthlyVoteAttendance, PersonMonthlyVoteAttendance
from parlacards.scores.common import get_dates_between, get_fortnights_between
from parladata.models.ballot import Ballot
from parladata.models.common import Mandate
from parladata.models.vote import Vote


def calculate_person_monthly_vote_attendance(person, playing_field, timestamp=None):
    """
    Returns monthly ballots count of voter
    """
    if not timestamp:
        timestamp = datetime.now()

    mandate = Mandate.get_active_mandate_at(timestamp)

    data = []

    ballots = (
        Ballot.objects.filter(
            personvoter=person,
            vote__timestamp__lte=timestamp,
            vote__motion__session__mandate=mandate,
            vote__motion__session__organizations=playing_field,
        )
        .annotate(month=TruncMonth("vote__timestamp"))
        .values("month", "option")
        .annotate(ballot_count=Count("option"))
        .order_by("month")
    )
    ballots = list(
        ballots
    )  # force db lookup here to prevent lookups later and speed up code in loop

    votes = (
        Vote.objects.filter(
            timestamp__lte=timestamp,
            motion__session__organizations=playing_field,
            motion__session__mandate=mandate,
        )
        .exclude(ballots__isnull=True)
        .exclude(ballots__personvoter__isnull=True)
        .annotate(
            month=TruncMonth("timestamp"),
        )
        .values("month")
        .annotate(total_votes=Count("id"))
        .order_by("month")
    )
    votes = list(
        votes
    )  # force db lookup here to prevent lookups later and speed up code in loop

    voter_memberships = person.person_memberships.filter(
        role="voter",
        organization=playing_field,
    )

    anonymous_votes = Vote.objects.none()

    for membership in voter_memberships:
        end_time = timestamp
        if membership.end_time:
            end_time = min([membership.end_time, timestamp])

        membership_anonymous_votes = (
            Vote.objects.filter(
                timestamp__lte=end_time,
                motion__session__organizations=playing_field,
                motion__session__mandate=mandate,
                ballots__personvoter__isnull=True,
            )
            .exclude(ballots__isnull=True)
            .distinct("id")
        )

        if membership.start_time:
            membership_anonymous_votes = membership_anonymous_votes.filter(
                timestamp__gte=membership.start_time
            )

        anonymous_votes = anonymous_votes.union(membership_anonymous_votes)

    # new query because union and annotate don't work together
    anonymous_votes = (
        Vote.objects.filter(
            id__in=anonymous_votes.values("id"),
        )
        .annotate(
            month=TruncMonth("timestamp"),
        )
        .values(
            "month",
        )
        .annotate(
            total_votes=Count("id"),
        )
        .order_by(
            "month",
        )
    )
    anonymous_votes = list(
        anonymous_votes
    )  # force db lookup here to prevent lookups later and speed up code in loop

    months = sorted(
        set(
            [
                *map(lambda v: v["month"], votes),
                *map(lambda v: v["month"], anonymous_votes),
            ]
        )
    )

    for month in months:
        monthly_anon_votes = next(
            filter(lambda v: v["month"] == month, anonymous_votes), None
        )
        monthly_votes = next(filter(lambda v: v["month"] == month, votes), None)

        total_votes = 0
        num_anon_votes = 0
        if monthly_votes:
            total_votes += monthly_votes["total_votes"]
        if monthly_anon_votes:
            num_anon_votes = monthly_anon_votes["total_votes"]
            total_votes += num_anon_votes

        temp_data = {
            "timestamp": month.isoformat(),
            "absent": 0,
            "abstain": 0,
            "for": 0,
            "against": 0,
            "no_data": num_anon_votes,
            "total": total_votes,
        }

        monthly_sums = filter(lambda v: v["month"] == month, ballots)
        for sums in monthly_sums:
            temp_data[sums["option"]] = sums["ballot_count"]

        data.append(temp_data)

    return data


def save_person_monthly_vote_attendance(person, playing_field, timestamp=None):
    if not timestamp:
        timestamp = datetime.now()

    monthly_results = calculate_person_monthly_vote_attendance(
        person, playing_field, timestamp
    )
    for result in monthly_results:
        if result["total"] > 0:
            present_count = result["for"] + result["abstain"] + result["against"]
            absent_count = result["absent"]
            anonymous_count = result["no_data"]
            person_votes_count = present_count + absent_count + anonymous_count

            no_mandate = (result["total"] - person_votes_count) / result["total"] * 100
            no_data = anonymous_count / result["total"] * 100
            present = present_count / result["total"] * 100

            score, created = PersonMonthlyVoteAttendance.objects.update_or_create(
                person=person,
                timestamp=result["timestamp"],
                playing_field=playing_field,
                defaults={
                    "no_mandate": no_mandate,
                    "no_data": no_data,
                    "value": present,
                },
            )


def save_people_monthly_vote_attendance(playing_field, timestamp=None):
    if not timestamp:
        timestamp = datetime.now()

    people = playing_field.query_voters(timestamp)

    for person in people:
        save_person_monthly_vote_attendance(person, playing_field, timestamp)


def save_people_monthly_vote_attendance_between(
    playing_field, datetime_from=None, datetime_to=None
):
    if not datetime_from:
        datetime_from = datetime.now()
    if not datetime_to:
        datetime_to = datetime.now()

    for day in get_dates_between(datetime_from, datetime_to):
        save_people_monthly_vote_attendance(playing_field, timestamp=day)


def save_sparse_people_monthly_vote_attendance_between(
    playing_field, datetime_from=None, datetime_to=None
):
    if not datetime_from:
        datetime_from = datetime.now()
    if not datetime_to:
        datetime_to = datetime.now()

    for day in get_fortnights_between(datetime_from, datetime_to):
        save_people_monthly_vote_attendance(playing_field, timestamp=day)


# GROUPS


def calculate_group_monthly_vote_attendance(group, playing_field, timestamp=None):
    """
    Returns monthly ballots count of voter
    """
    if not timestamp:
        timestamp = datetime.now()

    mandate = Mandate.get_active_mandate_at(timestamp)

    data = []

    memberships = group.query_memberships_before(timestamp)
    member_ids = memberships.values_list("member_id", flat=True).distinct("member_id")

    all_valid_ballots = Ballot.objects.none()
    all_annotated_anonymous_votes = []

    for member_id in member_ids:
        member_memberships = memberships.filter(
            member__id=member_id,
        ).values(
            "start_time",
            "end_time",
        )

        ballot_q_object = Q()
        vote_q_object = Q()
        for membership in member_memberships:
            ballot_q_params = {}
            vote_q_params = {}
            if membership["start_time"]:
                ballot_q_params["vote__timestamp__gte"] = membership["start_time"]
                vote_q_params["timestamp__gte"] = membership["start_time"]
            if membership["end_time"]:
                ballot_q_params["vote__timestamp__lte"] = membership["end_time"]
                vote_q_params["timestamp__lte"] = membership["end_time"]

            ballot_q_object.add(Q(**ballot_q_params), Q.OR)
            vote_q_object.add(Q(**vote_q_params), Q.OR)

        member_ballots = Ballot.objects.filter(
            vote__timestamp__lte=timestamp,
            vote__motion__session__organizations=playing_field,
            vote__motion__session__mandate=mandate,
            personvoter__id=member_id,
        ).filter(ballot_q_object)

        member_anonymous_votes = (
            Vote.objects.filter(
                timestamp__lte=timestamp,
                motion__session__organizations=playing_field,
                motion__session__mandate=mandate,
            )
            .exclude(id__in=member_ballots.distinct("vote").values("vote__id"))
            .filter(vote_q_object)
        )

        all_valid_ballots = all_valid_ballots.union(member_ballots)

        annotated_anonymous_votes = (
            member_anonymous_votes.annotate(
                month=TruncMonth("timestamp"),
            )
            .values(
                "month",
            )
            .annotate(
                total_votes=Count("id"),  # len(member_ids)
            )
            .order_by(
                "month",
            )
        )
        all_annotated_anonymous_votes = all_annotated_anonymous_votes + list(
            annotated_anonymous_votes
        )

    annotated_ballots = (
        Ballot.objects.filter(id__in=all_valid_ballots.values("id"))
        .annotate(month=TruncMonth("vote__timestamp"))
        .values("month", "option")
        .annotate(
            ballot_count=Count("option"),
        )
        .order_by("month")
    )
    annotated_ballots = list(
        annotated_ballots
    )  # force db lookup here to prevent lookups later and speed up code in loop

    months = sorted(
        set(
            [
                *map(lambda v: v["month"], annotated_ballots),
                *map(lambda v: v["month"], all_annotated_anonymous_votes),
            ]
        )
    )

    for month in months:
        monthly_anon_votes = list(
            filter(lambda v: v["month"] == month, all_annotated_anonymous_votes)
        )
        monthly_ballots = list(filter(lambda v: v["month"] == month, annotated_ballots))

        total_ballots = 0
        num_anon_ballots = 0
        if monthly_ballots:
            total_ballots += sum(map(lambda v: v["ballot_count"], monthly_ballots))
        if monthly_anon_votes:
            num_anon_ballots += sum(map(lambda v: v["total_votes"], monthly_anon_votes))

        temp_data = {
            "timestamp": month.isoformat(),
            "absent": 0,
            "abstain": 0,
            "for": 0,
            "against": 0,
            "no_data": num_anon_ballots,
            "total": total_ballots + num_anon_ballots,
        }

        for sums in monthly_ballots:
            temp_data[sums["option"]] = sums["ballot_count"]

        data.append(temp_data)

    return data


def save_group_monthly_vote_attendance(group, playing_field, timestamp=None):
    if not timestamp:
        timestamp = datetime.now()

    monthly_results = calculate_group_monthly_vote_attendance(
        group, playing_field, timestamp
    )
    for result in monthly_results:
        if result["total"] > 0:
            present_count = result["for"] + result["abstain"] + result["against"]
            absent_count = result["absent"]
            anonymous_count = result["no_data"]
            group_votes_count = present_count + absent_count + anonymous_count

            no_mandate = (result["total"] - group_votes_count) / result["total"] * 100
            no_data = anonymous_count / result["total"] * 100
            present = present_count / result["total"] * 100

            score, created = GroupMonthlyVoteAttendance.objects.update_or_create(
                group=group,
                timestamp=result["timestamp"],
                playing_field=playing_field,
                defaults={
                    "no_mandate": no_mandate,
                    "no_data": no_data,
                    "value": present,
                },
            )


def save_groups_monthly_vote_attendance(playing_field, timestamp=None):
    if not timestamp:
        timestamp = datetime.now()

    groups = playing_field.query_parliamentary_groups(timestamp)

    for group in groups:
        save_group_monthly_vote_attendance(group, playing_field, timestamp)


def save_groups_monthly_vote_attendance_between(
    playing_field, datetime_from=None, datetime_to=None
):
    if not datetime_from:
        datetime_from = datetime.now()
    if not datetime_to:
        datetime_to = datetime.now()

    for day in get_dates_between(datetime_from, datetime_to):
        save_groups_monthly_vote_attendance(playing_field, timestamp=day)


def save_sparse_groups_monthly_vote_attendance_between(
    playing_field, datetime_from=None, datetime_to=None
):
    if not datetime_from:
        datetime_from = datetime.now()
    if not datetime_to:
        datetime_to = datetime.now()

    for day in get_fortnights_between(datetime_from, datetime_to):
        save_groups_monthly_vote_attendance(playing_field, timestamp=day)
