from collections import Counter
from datetime import datetime

from parlacards.models import GroupStyleScore, PersonStyleScore
from parlacards.scores.common import (
    get_dates_between,
    get_fortnights_between,
    remove_punctuation,
    tokenize,
)
from parladata.models.common import Mandate
from parladata.models.speech import Speech


def get_styled_lemmas(style):
    # TODO current work directory?
    with open(f"parlacards/scores/styled_lemmas/{style}.csv", "r") as infile:
        return [line.strip() for line in infile.readlines()]


def calculate_style_score(speeches, styled_lemmas):
    # if there are no speeches return 0
    if speeches.count() == 0:
        return 0

    word_counter = Counter()
    styled_words_counter = Counter()

    for speech in speeches:
        # if there is no lemmatized_content we should bail
        # the data is not ready to run this analysis
        if not speech:
            raise ValueError("Lemmatized speech is missing.")
        for token in speech.strip().lower().split(" "):
            word_counter[token] += 1
            if token in styled_lemmas:
                styled_words_counter[token] += 1

    # return percentage of styled words
    return len(styled_words_counter.keys()) / len(word_counter.keys()) * 100


#
# PERSON
#
def save_person_style_scores(person, playing_field, timestamp=None):
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

    for style in ["problematic", "simple", "sophisticated"]:
        PersonStyleScore(
            person=person,
            value=calculate_style_score(speeches, get_styled_lemmas(style)),
            style=style,
            timestamp=timestamp,
            playing_field=playing_field,
        ).save()


def save_people_style_scores(playing_field, timestamp=None):
    if not timestamp:
        timestamp = datetime.now()

    people = playing_field.query_voters(timestamp)

    for person in people:
        save_person_style_scores(person, playing_field, timestamp)


def save_people_style_scores_between(
    playing_field, datetime_from=None, datetime_to=None
):
    if not datetime_from:
        datetime_from = datetime.now()
    if not datetime_to:
        datetime_to = datetime.now()

    for day in get_dates_between(datetime_from, datetime_to):
        save_people_style_scores(playing_field, timestamp=day)


def save_sparse_people_style_scores_between(
    playing_field, datetime_from=None, datetime_to=None
):
    if not datetime_from:
        datetime_from = datetime.now()
    if not datetime_to:
        datetime_to = datetime.now()

    for day in get_fortnights_between(datetime_from, datetime_to):
        save_people_style_scores(playing_field, timestamp=day)


#
# GROUP
#
def save_group_style_scores(group, playing_field, timestamp=None):
    if not timestamp:
        timestamp = datetime.now()

    mandate = Mandate.get_active_mandate_at(timestamp)

    # get speeches that started before the timestamp
    speeches = (
        Speech.objects.filter_valid_speeches(timestamp)
        .filter(
            speaker__id__in=group.query_members(timestamp).values("id"),
            start_time__lte=timestamp,
            session__mandate=mandate,
        )
        .values_list("lemmatized_content", flat=True)
    )
    # TODO what if there is no lemmatized content

    for style in ["problematic", "simple", "sophisticated"]:
        GroupStyleScore(
            group=group,
            value=calculate_style_score(speeches, get_styled_lemmas(style)),
            style=style,
            timestamp=timestamp,
            playing_field=playing_field,
        ).save()


def save_groups_style_scores(playing_field, timestamp=None):
    if not timestamp:
        timestamp = datetime.now()

    groups = playing_field.query_organization_members(timestamp).order_by("id")

    for group in groups:
        save_group_style_scores(group, playing_field, timestamp)


def save_groups_style_scores_between(
    playing_field, datetime_from=None, datetime_to=None
):
    if not datetime_from:
        datetime_from = datetime.now()
    if not datetime_to:
        datetime_to = datetime.now()

    for day in get_dates_between(datetime_from, datetime_to):
        save_groups_style_scores(playing_field, timestamp=day)


def save_sparse_groups_style_scores_between(
    playing_field, datetime_from=None, datetime_to=None
):
    if not datetime_from:
        datetime_from = datetime.now()
    if not datetime_to:
        datetime_to = datetime.now()

    for day in get_fortnights_between(datetime_from, datetime_to):
        save_groups_style_scores(playing_field, timestamp=day)
