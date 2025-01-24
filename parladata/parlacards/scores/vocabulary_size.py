from collections import Counter
from datetime import datetime

from django.db.models import Q

from parlacards.models import GroupVocabularySize, PersonVocabularySize
from parlacards.scores.common import (
    get_dates_between,
    get_fortnights_between,
    remove_punctuation,
    tokenize,
)
from parladata.models.common import Mandate
from parladata.models.speech import Speech


# TODO we should lemmatize speeches at import time
def calculate_vocabulary_size(speeches):
    # if there are no speeches return 0
    if speeches.count() == 0:
        return 0

    word_counter = Counter()

    for speech in speeches:
        # if there is no lemmatized_content we should bail
        # the data is not ready to run this analysis
        if not speech:
            raise ValueError("Lemmatized speech is missing.")
        for lemmatized_token in speech.strip().lower().split(" "):
            word_counter[lemmatized_token] += 1

    number_of_unique_words = len(word_counter.keys())

    frequency_counter = Counter()

    for frequency in word_counter.values():
        frequency_counter[str(frequency)] += 1

    return number_of_unique_words / (
        sum(
            [
                (frequency_counter[frequency] + (int(frequency) ** 2))
                for frequency in frequency_counter.keys()
            ]
        )
    )


#
# PERSON
#
def save_person_vocabulary_size(person, playing_field, timestamp=None):
    if not timestamp:
        timestamp = datetime.now()

    mandate = Mandate.get_active_mandate_at(timestamp)

    # get speeches that started before the timestamp
    speeches = (
        Speech.objects.filter_valid_speeches(timestamp)
        .filter(speaker=person, start_time__lte=timestamp, session__mandate=mandate)
        .values_list("lemmatized_content", flat=True)
    )
    # TODO what if there is no lemmatized content

    PersonVocabularySize(
        person=person,
        value=calculate_vocabulary_size(speeches),
        timestamp=timestamp,
        playing_field=playing_field,
    ).save()


def save_people_vocabulary_sizes(playing_field, timestamp=None):
    if not timestamp:
        timestamp = datetime.now()

    people = playing_field.query_voters(timestamp)

    for person in people:
        save_person_vocabulary_size(person, playing_field, timestamp)


def save_people_vocabulary_sizes_between(
    playing_field, datetime_from=None, datetime_to=None
):
    if not datetime_from:
        datetime_from = datetime.now()
    if not datetime_to:
        datetime_to = datetime.now()

    for day in get_dates_between(datetime_from, datetime_to):
        save_people_vocabulary_sizes(playing_field, timestamp=day)


def save_sparse_people_vocabulary_sizes_between(
    playing_field, datetime_from=None, datetime_to=None
):
    if not datetime_from:
        datetime_from = datetime.now()
    if not datetime_to:
        datetime_to = datetime.now()

    for day in get_fortnights_between(datetime_from, datetime_to):
        save_people_vocabulary_sizes(playing_field, timestamp=day)


#
# GROUP
#
def save_group_vocabulary_size(group, playing_field, timestamp=None):
    if not timestamp:
        timestamp = datetime.now()

    memberships = group.query_memberships_before(timestamp)
    member_ids = memberships.values_list("member_id", flat=True).distinct("member_id")

    mandate = Mandate.get_active_mandate_at(timestamp)

    speeches = Speech.objects.none()

    for member_id in member_ids:
        member_speeches = Speech.objects.filter_valid_speeches(
            timestamp,
        ).filter(
            speaker__id=member_id, start_time__lte=timestamp, session__mandate=mandate
        )

        member_memberships = memberships.filter(member__id=member_id).values(
            "start_time", "end_time"
        )

        q_objects = Q()

        for membership in member_memberships:
            q_params = {}
            if membership["start_time"]:
                q_params["start_time__gte"] = membership["start_time"]
            if membership["end_time"]:
                q_params["start_time__lte"] = membership["end_time"]
            q_objects.add(Q(**q_params), Q.OR)

        speeches = speeches.union(member_speeches.filter(q_objects))

    speech_contents = speeches.values_list("content", flat=True)

    GroupVocabularySize(
        group=group,
        value=calculate_vocabulary_size(speech_contents),
        timestamp=timestamp,
        playing_field=playing_field,
    ).save()


def save_groups_vocabulary_sizes(playing_field, timestamp=None):
    if not timestamp:
        timestamp = datetime.now()

    groups = playing_field.query_parliamentary_groups(timestamp)

    for group in groups:
        save_group_vocabulary_size(group, playing_field, timestamp)


def save_groups_vocabulary_sizes_between(
    playing_field, datetime_from=None, datetime_to=None
):
    if not datetime_from:
        datetime_from = datetime.now()
    if not datetime_to:
        datetime_to = datetime.now()

    for day in get_dates_between(datetime_from, datetime_to):
        save_groups_vocabulary_sizes(playing_field, timestamp=day)


def save_sparse_groups_vocabulary_sizes_between(
    playing_field, datetime_from=None, datetime_to=None
):
    if not datetime_from:
        datetime_from = datetime.now()
    if not datetime_to:
        datetime_to = datetime.now()

    for day in get_fortnights_between(datetime_from, datetime_to):
        save_groups_vocabulary_sizes(playing_field, timestamp=day)
