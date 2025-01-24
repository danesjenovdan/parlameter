from datetime import datetime

import pytest

from parlacards.scores.number_of_spoken_words import calculate_number_of_spoken_words
from parladata.models.speech import Speech
from tests.fixtures.common import *


@pytest.mark.django_db()
def test_calculate_number_of_spoken_words(
    first_person, second_person, last_person, ending_date_of_first_mandate
):
    timestamp = ending_date_of_first_mandate

    first_person_speeches = (
        Speech.objects.filter_valid_speeches(timestamp)
        .filter(speaker=first_person, start_time__lte=timestamp)
        .values_list("lemmatized_content", flat=True)
    )

    second_person_speeches = (
        Speech.objects.filter_valid_speeches(timestamp)
        .filter(speaker=second_person, start_time__lte=timestamp)
        .values_list("lemmatized_content", flat=True)
    )

    last_person_speeches = (
        Speech.objects.filter_valid_speeches(timestamp)
        .filter(speaker=last_person, start_time__lte=timestamp)
        .values_list("lemmatized_content", flat=True)
    )

    number_of_spoken_words = calculate_number_of_spoken_words(first_person_speeches)
    assert number_of_spoken_words == 1480

    number_of_spoken_words = calculate_number_of_spoken_words(second_person_speeches)
    assert number_of_spoken_words == 981

    number_of_spoken_words = calculate_number_of_spoken_words(last_person_speeches)
    assert number_of_spoken_words == 0
