from datetime import datetime

from django.db.models import Q

from parlacards.models import GroupAvgSpeechesPerSession, PersonAvgSpeechesPerSession
from parlacards.scores.common import get_dates_between, get_fortnights_between
from parladata.models.ballot import Ballot
from parladata.models.common import Mandate
from parladata.models.session import Session
from parladata.models.speech import Speech


def calculate_person_avg_number_of_speeches(person, timestamp=None):
    if not timestamp:
        timestamp = datetime.now()

    mandate = Mandate.get_active_mandate_at(timestamp)

    person_speeches = Speech.objects.filter_valid_speeches(timestamp).filter(
        speaker=person, start_time__lte=timestamp, session__mandate=mandate
    )
    num_of_speeches = person_speeches.count()

    ballot_session_ids = (
        Ballot.objects.filter(
            personvoter=person,
            vote__timestamp__lte=timestamp,
            vote__motion__session__mandate=mandate,
        )
        .distinct("vote__motion__session__id")
        .values_list("vote__motion__session__id", flat=True)
    )

    speech_session_ids = person_speeches.distinct("session__id").values_list(
        "session__id", flat=True
    )

    no_of_sessions_with_activity = len(
        set(ballot_session_ids).union(set(speech_session_ids))
    )

    if no_of_sessions_with_activity == 0:
        return 0
    else:
        return num_of_speeches / no_of_sessions_with_activity


def save_person_avg_number_of_speeches_per_session(
    person, playing_field, timestamp=None
):
    if not timestamp:
        timestamp = datetime.now()

    PersonAvgSpeechesPerSession(
        person=person,
        value=calculate_person_avg_number_of_speeches(person, timestamp),
        timestamp=timestamp,
        playing_field=playing_field,
    ).save()


def save_people_avg_number_of_speeches_per_session(playing_field, timestamp=None):
    if not timestamp:
        timestamp = datetime.now()

    people = playing_field.query_voters(timestamp)

    for person in people:
        save_person_avg_number_of_speeches_per_session(person, playing_field, timestamp)


def save_people_avg_number_of_speeches_per_session_between(
    playing_field, datetime_from=None, datetime_to=None
):
    if not datetime_from:
        datetime_from = datetime.now()
    if not datetime_to:
        datetime_to = datetime.now()

    for day in get_dates_between(datetime_from, datetime_to):
        save_people_avg_number_of_speeches_per_session(playing_field, timestamp=day)


def save_sparse_people_avg_number_of_speeches_per_session_between(
    playing_field, datetime_from=None, datetime_to=None
):
    if not datetime_from:
        datetime_from = datetime.now()
    if not datetime_to:
        datetime_to = datetime.now()

    for day in get_fortnights_between(datetime_from, datetime_to):
        save_people_avg_number_of_speeches_per_session(playing_field, timestamp=day)


# Groups
def calculate_group_avg_number_of_speeches(group, timestamp=datetime.now()):
    member_ids = group.query_members(timestamp).values_list("id", flat=True)
    memberships = group.query_memberships_before(timestamp)

    speeches = Speech.objects.none()
    ballots = Ballot.objects.none()

    for member_id in member_ids:
        member_speeches = Speech.objects.filter_valid_speeches(timestamp).filter(
            speaker_id=member_id,
            start_time__lte=timestamp,
        )

        member_ballots = Ballot.objects.filter(
            personvoter_id=member_id,
            vote__timestamp__lte=timestamp,
        )

        member_memberships = memberships.filter(member__id=member_id).values(
            "start_time", "end_time"
        )

        q_speech_objects = Q()
        q_ballot_objects = Q()

        for membership in member_memberships:
            q_speech_params = {}
            q_ballots_params = {}
            if membership["start_time"]:
                q_speech_params["start_time__gte"] = membership["start_time"]
                q_ballots_params["vote__timestamp__gte"] = membership["start_time"]
            if membership["end_time"]:
                q_speech_params["start_time__lte"] = membership["end_time"]
                q_ballots_params["vote__timestamp__lte"] = membership["end_time"]
            q_speech_objects.add(Q(**q_speech_params), Q.OR)
            q_ballot_objects.add(Q(**q_ballots_params), Q.OR)

        speeches = speeches.union(member_speeches.filter(q_speech_objects))
        ballots = ballots.union(member_ballots.filter(q_ballot_objects))

    num_of_speeches = speeches.count()

    ballot_session_ids = ballots.values_list("vote__motion__session__id", flat=True)

    speech_session_ids = speeches.values_list("session__id", flat=True)

    no_of_sessions_with_activity = len(
        set(ballot_session_ids).union(set(speech_session_ids))
    )

    if no_of_sessions_with_activity == 0:
        return 0
    else:
        return num_of_speeches / no_of_sessions_with_activity


def save_group_avg_number_of_speeches_per_session(
    group, playing_field, timestamp=datetime.now()
):
    GroupAvgSpeechesPerSession(
        group=group,
        value=calculate_group_avg_number_of_speeches(group, timestamp),
        timestamp=timestamp,
        playing_field=playing_field,
    ).save()


def save_groups_avg_number_of_speeches_per_session(
    playing_field, timestamp=datetime.now()
):
    groups = playing_field.query_parliamentary_groups(timestamp)

    for group in groups:
        save_group_avg_number_of_speeches_per_session(group, playing_field, timestamp)


def save_group_avg_number_of_speeches_per_session_between(
    playing_field, datetime_from=datetime.now(), datetime_to=datetime.now()
):
    for day in get_dates_between(datetime_from, datetime_to):
        save_groups_avg_number_of_speeches_per_session(playing_field, timestamp=day)


def save_sparse_group_avg_number_of_speeches_per_session_between(
    playing_field, datetime_from=datetime.now(), datetime_to=datetime.now()
):
    for day in get_fortnights_between(datetime_from, datetime_to):
        save_groups_avg_number_of_speeches_per_session(playing_field, timestamp=day)
