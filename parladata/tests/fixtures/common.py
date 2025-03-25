from datetime import datetime, timedelta

import pytest

from parladata.models.common import Mandate
from parladata.models.organization import Organization
from parladata.models.vote import Vote


@pytest.fixture
def main_organization():
    return Organization.objects.order_by("id").first()


@pytest.fixture
def first_mandate():
    return Mandate.objects.order_by("id").first()


@pytest.fixture
def coalition(main_organization):
    return (
        main_organization.query_organization_members()
        .filter(classification="coalition")
        .first()
    )


@pytest.fixture
def ending_date_of_first_mandate(first_mandate):
    return first_mandate.ending - timedelta(days=1)


@pytest.fixture
def first_person(main_organization, ending_date_of_first_mandate):
    return (
        main_organization.query_voters(ending_date_of_first_mandate)
        .order_by("id")
        .first()
    )


@pytest.fixture
def second_person(main_organization, ending_date_of_first_mandate):
    return main_organization.query_voters(ending_date_of_first_mandate).order_by("id")[
        2
    ]


@pytest.fixture
def last_person(main_organization, ending_date_of_first_mandate):
    return (
        main_organization.query_voters(ending_date_of_first_mandate)
        .order_by("id")
        .last()
    )


@pytest.fixture
def first_group(main_organization, ending_date_of_first_mandate):
    return (
        main_organization.query_parliamentary_groups(ending_date_of_first_mandate)
        .order_by("id")
        .first()
    )


@pytest.fixture
def second_group(main_organization, ending_date_of_first_mandate):
    return main_organization.query_parliamentary_groups(
        ending_date_of_first_mandate
    ).order_by("id")[2]


@pytest.fixture
def last_group(main_organization, ending_date_of_first_mandate):
    return (
        main_organization.query_parliamentary_groups(ending_date_of_first_mandate)
        .order_by("id")
        .last()
    )


@pytest.fixture
def first_vote():
    return (
        Vote.objects.first()
    )


@pytest.fixture
def first_session(main_organization):
    return main_organization.sessions.first()


# fixtures for views
@pytest.fixture
def first_mandate_params():
    return {
        "id": "1",
        "date": "2019-11-29",
    }


@pytest.fixture
def current_mandate_params():
    return {
        "id": "2",
    }


@pytest.fixture
def current_root_org():
    return {
        "id": "48",
    }


@pytest.fixture
def first_root_org():
    return {
        "id": "1",
    }


@pytest.fixture
def first_mandate_party():
    return {
        "id": "19",
    }


@pytest.fixture
def all_mandate_party():
    return {
        "id": "20",
    }


@pytest.fixture
def first_mandate_member():
    return {
        "id": "240",
    }


@pytest.fixture
def all_mandate_member():
    return {
        "id": "245",
    }


@pytest.fixture
def bicameral_org_1():
    return {
        "id": "18",
    }


@pytest.fixture
def bicameral_org_2():
    return {
        "id": "55",
    }


@pytest.fixture
def bicameral_person_1():
    return {
        "id": "431",
    }


@pytest.fixture
def bicameral_person_2():
    return {
        "id": "424",
    }
