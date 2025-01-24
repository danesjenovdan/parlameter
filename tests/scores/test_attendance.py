import pytest

from parlacards.scores.attendance import (
    calculate_group_vote_attendance,
    calculate_person_vote_attendance,
)
from tests.fixtures.common import *


@pytest.mark.django_db()
def test_calculate_person_vote_attendance(
    first_person,
    second_person,
    last_person,
    ending_date_of_first_mandate,
    main_organization,
):
    attendance = calculate_person_vote_attendance(
        first_person, main_organization, ending_date_of_first_mandate
    )
    assert attendance == 62.5

    attendance = calculate_person_vote_attendance(
        second_person, main_organization, ending_date_of_first_mandate
    )
    assert attendance == 55.0

    attendance = calculate_person_vote_attendance(
        last_person, main_organization, ending_date_of_first_mandate
    )
    assert attendance == 0


@pytest.mark.django_db()
def test_calculate_group_vote_attendance(
    first_group, last_group, ending_date_of_first_mandate, main_organization
):
    attendance = calculate_group_vote_attendance(
        first_group, main_organization, ending_date_of_first_mandate
    )
    assert attendance == 58.75

    attendance = calculate_group_vote_attendance(
        last_group, main_organization, ending_date_of_first_mandate
    )
    assert attendance == 93.91304347826087
