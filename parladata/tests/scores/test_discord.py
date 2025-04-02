import pytest

from parlacards.scores.discord import (
    calculate_group_discord,
    calculate_organization_vote_discord,
)
from tests.fixtures.common import *


@pytest.mark.django_db()
def test_calculate_voting_distance(
    first_group, second_group, last_group, ending_date_of_first_mandate
):
    # group
    discord = calculate_group_discord(first_group, ending_date_of_first_mandate)
    assert discord == 8.75

    discord = calculate_group_discord(second_group, ending_date_of_first_mandate)
    assert discord == 29.999999999999993

    discord = calculate_group_discord(last_group, ending_date_of_first_mandate)
    assert discord == 8.804347826086957


@pytest.mark.django_db()
def test_calculate_organization_vote_discord(
    first_vote, main_organization, coalition, first_group, second_group, last_group
):

    # group
    discord = calculate_organization_vote_discord(
        first_vote, first_group, main_organization, main_organization, None
    )
    assert discord == 100

    discord = calculate_organization_vote_discord(
        first_vote, second_group, main_organization, main_organization, None
    )
    assert discord == 66.66666666666666

    discord = calculate_organization_vote_discord(
        first_vote, coalition, main_organization, main_organization, coalition
    )
    assert discord == 95.65217391304348

    discord = calculate_organization_vote_discord(
        first_vote, last_group, main_organization, main_organization, None
    )
    assert discord == 95.65217391304348
