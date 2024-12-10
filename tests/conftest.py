import pytest
from django.core.management import call_command

from parladata.models.organization import Organization
from parladata.models.person import Person


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command("loaddata", "tests/fixtures/test_db.json")
