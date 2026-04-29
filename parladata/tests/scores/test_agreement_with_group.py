import pytest

from parlacards.scores.agreement_with_group import calculate_agreement_with_group
from tests.fixtures.common import *


@pytest.mark.django_db()
def test_calculate_agreement_with_group(
    first_person,
    second_person,
    last_person,
    main_organization,
    ending_date_of_first_mandate,
):
    agreement = calculate_agreement_with_group(
        first_person, main_organization, ending_date_of_first_mandate
    )
    assert agreement == 95

    agreement = calculate_agreement_with_group(
        second_person, main_organization, ending_date_of_first_mandate
    )
    assert agreement == 87.5

    agreement = calculate_agreement_with_group(
        last_person, main_organization, ending_date_of_first_mandate
    )
    assert agreement == 100
