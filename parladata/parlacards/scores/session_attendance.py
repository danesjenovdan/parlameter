from collections import Counter
from datetime import datetime

from django.db.models import Q

from parlacards.models import SessionGroupAttendance
from parlacards.scores.common import get_dates_between, get_fortnights_between
from parladata.models.ballot import Ballot


def calculate_session_vote_attendance(session, group, timestamp=None):
    if not timestamp:
        timestamp = datetime.now()

    memberships = group.query_memberships_before(timestamp)
    member_ids = memberships.values_list("member_id", flat=True).distinct("member_id")

    ballots = Ballot.objects.none()

    for member_id in member_ids:
        member_ballots = Ballot.objects.filter(
            personvoter_id=member_id,
            vote__timestamp__lte=timestamp,
            vote__motion__session=session,
        )

        member_memberships = memberships.filter(member__id=member_id).values(
            "start_time", "end_time"
        )

        q_ballot_objects = Q()

        for membership in member_memberships:
            q_ballots_params = {}
            if membership["start_time"]:
                q_ballots_params["vote__timestamp__gte"] = membership["start_time"]
            if membership["end_time"]:
                q_ballots_params["vote__timestamp__lte"] = membership["end_time"]
            q_ballot_objects.add(Q(**q_ballots_params), Q.OR)

        ballots = ballots.union(member_ballots.filter(q_ballot_objects))

    # WORKAROUND because values_list of union returns distinct values
    ballot_options = [ballot.option for ballot in ballots]

    option_counter = Counter(ballot_options)

    ballots_for = option_counter.get("for", 0)
    ballots_against = option_counter.get("against", 0)
    ballots_abstain = option_counter.get("abstain", 0)
    ballots_absent = option_counter.get("absent", 0)

    present_ballots = ballots_for + ballots_against + ballots_abstain
    all_ballots = present_ballots + ballots_absent
    if all_ballots == 0:
        return 0
    else:
        return present_ballots * 100 / all_ballots


def save_group_vote_attendance_on_session(
    session, group, playing_field, timestamp=None
):
    if not timestamp:
        timestamp = datetime.now()

    session_attendance = SessionGroupAttendance.objects.filter(
        session=session, group=group, playing_field=playing_field
    )
    if session_attendance:
        session_attendance = session_attendance.first()
        session_attendance.value = calculate_session_vote_attendance(
            session, group, timestamp
        )
        session_attendance.save()
    else:
        SessionGroupAttendance(
            session=session,
            group=group,
            value=calculate_session_vote_attendance(session, group, timestamp),
            timestamp=session.start_time,
            playing_field=playing_field,
        ).save()


def save_groups_vote_attendance_on_session(session, playing_field, timestamp=None):
    if not timestamp:
        timestamp = datetime.now()

    groups = playing_field.query_parliamentary_groups(timestamp)
    for group in groups:
        save_group_vote_attendance_on_session(session, group, playing_field, timestamp)


def save_groups_vote_attendance_on_sessions(playing_field, timestamp=None):
    if not timestamp:
        timestamp = datetime.now()

    sessions = playing_field.sessions.filter(start_time__lte=timestamp)
    for session in sessions:
        save_groups_vote_attendance_on_session(session, playing_field, timestamp)


def save_groups_vote_attendance_on_session_between(
    playing_field, datetime_from=None, datetime_to=None
):
    if not datetime_from:
        datetime_from = datetime.now()
    if not datetime_to:
        datetime_to = datetime.now()

    for day in get_dates_between(datetime_from, datetime_to):
        save_groups_vote_attendance_on_sessions(playing_field, timestamp=day)


def save_sparse_groups_vote_attendance_on_session_between(
    playing_field, datetime_from=None, datetime_to=None
):
    if not datetime_from:
        datetime_from = datetime.now()
    if not datetime_to:
        datetime_to = datetime.now()

    for day in get_fortnights_between(datetime_from, datetime_to):
        save_groups_vote_attendance_on_sessions(playing_field, timestamp=day)
