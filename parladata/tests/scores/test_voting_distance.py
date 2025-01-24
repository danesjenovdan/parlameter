import pytest

from parlacards.scores.voting_distance import (
    calculate_group_voting_distance,
    calculate_voting_distance,
    calculate_voting_distance_between_groups,
)
from tests.fixtures.common import *


@pytest.mark.django_db()
def test_calculate_voting_distance(
    first_person,
    second_person,
    last_person,
    first_group,
    second_group,
    last_group,
    main_organization,
    ending_date_of_first_mandate,
):
    # person
    voting_distance = calculate_voting_distance(
        first_person, second_person, ending_date_of_first_mandate
    )
    assert voting_distance == 100.0

    voting_distance = calculate_voting_distance(
        second_person, first_person, ending_date_of_first_mandate
    )
    assert voting_distance == 100.0

    voting_distance = calculate_voting_distance(
        first_person, last_person, ending_date_of_first_mandate
    )
    assert voting_distance == 0.0

    voting_distance = calculate_voting_distance(
        second_person, last_person, ending_date_of_first_mandate
    )
    assert voting_distance == 0.0

    # group
    group_voting_distances = calculate_group_voting_distance(
        first_group, main_organization, ending_date_of_first_mandate
    )
    assert len(group_voting_distances) == 41
    assert group_voting_distances[217] == 100.0
    assert group_voting_distances[256] == 74.07407407407408
    assert group_voting_distances[244] == 69.23076923076923

    # THIS IS NOT USED BUT POSSIBLY INTERESTING
    voting_distance = calculate_voting_distance_between_groups(
        first_group, last_group, ending_date_of_first_mandate
    )
    assert voting_distance == 5.0

    voting_distance = calculate_voting_distance_between_groups(
        last_group, first_group, ending_date_of_first_mandate
    )
    assert voting_distance == 5.0

    voting_distance = calculate_voting_distance_between_groups(
        first_group, second_group, ending_date_of_first_mandate
    )
    assert voting_distance == 2.449489742783178

    voting_distance = calculate_voting_distance_between_groups(
        second_group, last_group, ending_date_of_first_mandate
    )
    assert voting_distance == 3.3166247903554
