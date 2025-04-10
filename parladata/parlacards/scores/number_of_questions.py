from datetime import datetime

from django.db.models import Q

from parlacards.models import GroupNumberOfQuestions, PersonNumberOfQuestions
from parlacards.scores.common import get_dates_between, get_fortnights_between
from parladata.models.common import Mandate
from parladata.models.question import Question


# People
def calculate_number_of_questions_from_person(person, timestamp=None):
    if not timestamp:
        timestamp = datetime.now()

    mandate = Mandate.get_active_mandate_at(timestamp)

    # from_timestamp, to_timestamp = mandate.get_time_range_from_mandate(timestamp)

    return Question.objects.filter(
        person_authors=person,
        mandate=mandate,
        # timestamp__lt=to_timestamp,
    ).count()


def save_number_of_questions_from_person(person, playing_field, timestamp=None):
    if not timestamp:
        timestamp = datetime.now()

    PersonNumberOfQuestions(
        person=person,
        value=calculate_number_of_questions_from_person(person, timestamp),
        timestamp=timestamp,
        playing_field=playing_field,
    ).save()


def save_people_number_of_questions(playing_field, timestamp=None):
    if not timestamp:
        timestamp = datetime.now()

    people = playing_field.query_voters(timestamp)

    for person in people:
        save_number_of_questions_from_person(person, playing_field, timestamp)


def save_people_number_of_questions_between(
    playing_field, datetime_from=None, datetime_to=None
):
    if not datetime_from:
        datetime_from = datetime.now()
    if not datetime_to:
        datetime_to = datetime.now()

    for day in get_dates_between(datetime_from, datetime_to):
        save_people_number_of_questions(playing_field, timestamp=day)


def save_sparse_people_number_of_questions_between(
    playing_field, datetime_from=None, datetime_to=None
):
    if not datetime_from:
        datetime_from = datetime.now()
    if not datetime_to:
        datetime_to = datetime.now()

    for day in get_fortnights_between(datetime_from, datetime_to):
        save_people_number_of_questions(playing_field, timestamp=day)


# Groups
def calculate_group_number_of_question(group, playing_field, timestamp=None):
    """
    Returns question count of group
    """
    if not timestamp:
        timestamp = datetime.now()

    mandate = Mandate.get_active_mandate_at(timestamp)

    # from_timestamp, to_timestamp = mandate.get_time_range_from_mandate(timestamp)

    memberships = group.query_memberships_before(timestamp)
    member_ids = memberships.values_list("member_id", flat=True).distinct("member_id")

    questions = Question.objects.none()

    for member_id in member_ids:
        member_questions = Question.objects.filter(
            mandate=mandate,
            person_authors__id=member_id,
        )

        member_memberships = memberships.filter(
            member__id=member_id, mandate=mandate
        ).values("start_time", "end_time")
        q_objects = Q()
        for membership in member_memberships:
            q_params = {}
            if membership["start_time"]:
                q_params["timestamp__gte"] = membership["start_time"]
            if membership["end_time"]:
                q_params["timestamp__lte"] = membership["end_time"]
            q_objects.add(Q(**q_params), Q.OR)

        organization_questions = Question.objects.filter(
            mandate=mandate,
        )

        questions = questions.union(organization_questions)

        questions = questions.union(member_questions.filter(q_objects))

    return questions.count()


def save_group_number_of_questions_for_group(group, playing_field, timestamp=None):
    if not timestamp:
        timestamp = datetime.now()

    questions_count = calculate_group_number_of_question(
        group, playing_field, timestamp
    )

    GroupNumberOfQuestions(
        group=group,
        value=questions_count,
        timestamp=timestamp,
        playing_field=playing_field,
    ).save()


def save_group_number_of_questions(playing_field, timestamp=None):
    if not timestamp:
        timestamp = datetime.now()

    groups = playing_field.query_parliamentary_groups(timestamp)

    for group in groups:
        save_group_number_of_questions_for_group(group, playing_field, timestamp)


def save_group_number_of_questions_between(
    playing_field, datetime_from=None, datetime_to=None
):
    if not datetime_from:
        datetime_from = datetime.now()
    if not datetime_to:
        datetime_to = datetime.now()

    for day in get_dates_between(datetime_from, datetime_to):
        save_group_number_of_questions(playing_field, timestamp=day)


def save_sparse_group_number_of_questions_between(
    playing_field, datetime_from=None, datetime_to=None
):
    if not datetime_from:
        datetime_from = datetime.now()
    if not datetime_to:
        datetime_to = datetime.now()

    for day in get_fortnights_between(datetime_from, datetime_to):
        save_group_number_of_questions(playing_field, timestamp=day)
