import pytest

from parlacards.scores.avg_number_of_speeches_per_session import (
    calculate_person_avg_number_of_speeches,
)
from tests.fixtures.common import *


@pytest.mark.django_db()
def test_calculate_person_avg_number_of_speeches(
    first_person, second_person, last_person, ending_date_of_first_mandate
):
    avg_number_of_speeches = calculate_person_avg_number_of_speeches(
        first_person, ending_date_of_first_mandate
    )
    assert avg_number_of_speeches == 6.0

    avg_number_of_speeches = calculate_person_avg_number_of_speeches(
        second_person, ending_date_of_first_mandate
    )
    assert avg_number_of_speeches == 5.5

    avg_number_of_speeches = calculate_person_avg_number_of_speeches(
        last_person, ending_date_of_first_mandate
    )
    assert avg_number_of_speeches == 0
