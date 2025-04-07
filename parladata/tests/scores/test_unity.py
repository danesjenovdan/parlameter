import pytest

from parlacards.scores.unity import (
    calculate_organization_vote_unity,
)
from tests.fixtures.common import *


@pytest.mark.django_db()
def test_calculate_organization_vote_unity(
    first_vote, main_organization, coalition, first_group, second_group, last_group
):

    # group
    unity = calculate_organization_vote_unity(
        first_vote, first_group, main_organization, main_organization, None
    )
    assert unity == 100

    unity = calculate_organization_vote_unity(
        first_vote, second_group, main_organization, main_organization, None
    )
    assert unity == 66.66666666666666

    unity = calculate_organization_vote_unity(
        first_vote, coalition, main_organization, main_organization, coalition
    )
    assert unity == 95.65217391304348

    unity = calculate_organization_vote_unity(
        first_vote, last_group, main_organization, main_organization, None
    )
    assert unity == 95.65217391304348
