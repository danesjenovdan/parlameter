import json

import pytest

from export.resources.misc import *
from export.resources.session import *
from tests.fixtures.common import *


class SessionResourceExportTest:
    resource = None
    headers = ["name", "value", "timestamp"]
    csv_results_count = 3
    json_results_count = 1

    @pytest.mark.django_db()
    def test_export_as_generator_json(self, first_mandate, first_session):
        resource = self.resource()
        generator = resource.export_as_generator_json(
            mandate_id=first_mandate.id, request_id=first_session.id
        )
        chunks = list(generator)
        chunks_joined = "".join(chunks)
        res = json.loads(chunks_joined)
        # check num of results
        assert len(res) == self.json_results_count
        # check keys
        if self.json_results_count > 0:
            json_keys = res[0].keys()

            for header in self.headers:
                assert header in json_keys

    @pytest.mark.django_db()
    def test_export_as_generator_csv(self, first_mandate, first_session):
        resource = self.resource()
        generator = resource.export_as_generator_csv(
            mandate_id=first_mandate.id, request_id=first_session.id
        )
        chunks = list(generator)
        chunks_joined = "".join(chunks)
        lines = chunks_joined.splitlines()
        headers = lines[0].split(",")
        # check num of results
        assert (
            len(lines) == self.csv_results_count
        )  # len(results) + headers + empty line
        # check headers
        for header in self.headers:
            assert header in headers


class TestVoteResource(SessionResourceExportTest):
    resource = VoteResource
    csv_results_count = 31
    json_results_count = 29
    headers = ["id", "name", "motion__text", "motion__summary", "result", "law_id"]


class TestLegislationResource(SessionResourceExportTest):
    resource = LegislationResource
    csv_results_count = 4
    json_results_count = 2
    headers = [
        "id",
        "text",
        "epa",
        "passed",
        "classification",
        "timestamp",
        "procedure_phase",
    ]
