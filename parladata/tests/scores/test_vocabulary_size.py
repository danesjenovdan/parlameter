from datetime import datetime

import pytest

from parlacards.scores.vocabulary_size import calculate_vocabulary_size
from parladata.models.speech import Speech
from tests.fixtures.common import *


@pytest.mark.django_db()
def test_calculate_vocabulary_size(
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

    vocabulary_size = calculate_vocabulary_size(first_person_speeches)
    assert vocabulary_size == 0.01561282589151933

    vocabulary_size = calculate_vocabulary_size(second_person_speeches)
    assert vocabulary_size == 0.03628015844436442

    vocabulary_size = calculate_vocabulary_size(last_person_speeches)
    assert vocabulary_size == 0
