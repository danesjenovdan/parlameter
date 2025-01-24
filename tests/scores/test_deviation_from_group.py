import pytest

from parlacards.scores.deviation_from_group import calculate_deviation_from_group
from tests.fixtures.common import *


@pytest.mark.django_db()
def test_calculate_deviation_from_group(
    first_person,
    second_person,
    last_person,
    main_organization,
    ending_date_of_first_mandate,
):
    deviation = calculate_deviation_from_group(
        first_person, main_organization, ending_date_of_first_mandate
    )
    assert deviation == 5

    deviation = calculate_deviation_from_group(
        second_person, main_organization, ending_date_of_first_mandate
    )
    assert deviation == 12.5

    deviation = calculate_deviation_from_group(
        last_person, main_organization, ending_date_of_first_mandate
    )
    assert deviation == 0
