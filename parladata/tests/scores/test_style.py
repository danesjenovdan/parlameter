from datetime import datetime

import pytest

from parlacards.scores.style import calculate_style_score, get_styled_lemmas
from parladata.models.speech import Speech
from tests.fixtures.common import *


@pytest.mark.django_db()
def test_calculate_style_scores(
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

    problematic_style = calculate_style_score(
        first_person_speeches, get_styled_lemmas("problematic")
    )
    simple_style = calculate_style_score(
        first_person_speeches, get_styled_lemmas("simple")
    )
    sophisticated_style = calculate_style_score(
        first_person_speeches, get_styled_lemmas("sophisticated")
    )

    assert problematic_style == 0.9596928982725527
    assert simple_style == 1.9193857965451053
    assert sophisticated_style == 3.45489443378119

    problematic_style = calculate_style_score(
        second_person_speeches, get_styled_lemmas("problematic")
    )
    simple_style = calculate_style_score(
        second_person_speeches, get_styled_lemmas("simple")
    )
    sophisticated_style = calculate_style_score(
        second_person_speeches, get_styled_lemmas("sophisticated")
    )

    assert problematic_style == 0.49627791563275436
    assert simple_style == 2.729528535980149
    assert sophisticated_style == 5.2109181141439205

    problematic_style = calculate_style_score(
        last_person_speeches, get_styled_lemmas("problematic")
    )
    simple_style = calculate_style_score(
        last_person_speeches, get_styled_lemmas("simple")
    )
    sophisticated_style = calculate_style_score(
        last_person_speeches, get_styled_lemmas("sophisticated")
    )

    assert problematic_style == 0
    assert simple_style == 0
    assert sophisticated_style == 0
