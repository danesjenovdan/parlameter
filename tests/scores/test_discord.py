import pytest

from parlacards.scores.discord import calculate_group_discord
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
