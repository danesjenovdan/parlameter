import pytest

from parlacards.scores.monthly_attendance import (
    calculate_person_monthly_vote_attendance,
)
from tests.fixtures.common import *


@pytest.mark.django_db()
def test_calculate_person_monthly_vote_attendance(
    first_person,
    second_person,
    last_person,
    main_organization,
    ending_date_of_first_mandate,
):
    monthly_attendance = calculate_person_monthly_vote_attendance(
        first_person, main_organization, ending_date_of_first_mandate
    )
    assert len(monthly_attendance) == 2
    assert sum([attendance["absent"] for attendance in monthly_attendance]) == 15
    assert sum([attendance["abstain"] for attendance in monthly_attendance]) == 1
    assert sum([attendance["for"] for attendance in monthly_attendance]) == 19
    assert sum([attendance["against"] for attendance in monthly_attendance]) == 5
    assert sum([attendance["no_data"] for attendance in monthly_attendance]) == 0
    assert sum([attendance["total"] for attendance in monthly_attendance]) == 40

    monthly_attendance = calculate_person_monthly_vote_attendance(
        second_person, main_organization, ending_date_of_first_mandate
    )
    assert sum([attendance["absent"] for attendance in monthly_attendance]) == 18
    assert sum([attendance["abstain"] for attendance in monthly_attendance]) == 1
    assert sum([attendance["for"] for attendance in monthly_attendance]) == 19
    assert sum([attendance["against"] for attendance in monthly_attendance]) == 2
    assert sum([attendance["no_data"] for attendance in monthly_attendance]) == 0
    assert sum([attendance["total"] for attendance in monthly_attendance]) == 40

    monthly_attendance = calculate_person_monthly_vote_attendance(
        last_person, main_organization, ending_date_of_first_mandate
    )
    assert sum([attendance["absent"] for attendance in monthly_attendance]) == 0
    assert sum([attendance["abstain"] for attendance in monthly_attendance]) == 0
    assert sum([attendance["for"] for attendance in monthly_attendance]) == 0
    assert sum([attendance["against"] for attendance in monthly_attendance]) == 0
    assert sum([attendance["no_data"] for attendance in monthly_attendance]) == 0
    assert sum([attendance["total"] for attendance in monthly_attendance]) == 40
