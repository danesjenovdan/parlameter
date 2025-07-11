import pytest

from parlacards.scores.unity import (
    calculate_group_unity,
)
from tests.fixtures.common import *


@pytest.mark.django_db()
def test_calculate_voting_distance(
    first_group, second_group, last_group, ending_date_of_first_mandate
):
    # group
    unity = calculate_group_unity(first_group, ending_date_of_first_mandate)
    assert unity == 8.75

    unity = calculate_group_unity(second_group, ending_date_of_first_mandate)
    assert unity == 29.999999999999993

    unity = calculate_group_unity(last_group, ending_date_of_first_mandate)
    assert unity == 8.804347826086957
