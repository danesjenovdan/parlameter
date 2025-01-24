import json

import pytest

from export.resources.misc import *
from tests.fixtures.common import *


class MiscResourceExportTest:
    resource = None
    headers = ["name", "value", "timestamp"]
    csv_results_count = 3
    json_results_count = 1

    @pytest.mark.django_db()
    def test_export_as_generator_json(self, first_mandate):
        resource = self.resource()
        generator = resource.export_as_generator_json(mandate_id=first_mandate.id)
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
    def test_export_as_generator_csv(self, first_mandate):
        resource = self.resource()
        generator = resource.export_as_generator_csv(mandate_id=first_mandate.id)
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


class TestMPResource(MiscResourceExportTest):
    resource = MPResource
    csv_results_count = 47
    json_results_count = 45
    headers = [
        "id",
        "name",
        "date_of_birth",
        "age",
        "education_level",
        "preferred_pronoun",
        "number_of_mandates",
        "speeches_per_session",
        "number_of_questions",
        "mismatch_of_pg",
        "presence_votes",
        "spoken_words",
        "vocabulary_size",
    ]


class TestGroupsResource(MiscResourceExportTest):
    resource = GroupsResource
    csv_results_count = 9
    json_results_count = 7
    headers = [
        "id",
        "name",
        "acronym",
        "number_of_members_at",
        "intra_disunion",
        "vocabulary_size",
        "number_of_questions",
        "vote_attendance",
    ]


class TestSessionResource(MiscResourceExportTest):
    resource = SessionResource
    csv_results_count = 4
    json_results_count = 2
    headers = [
        "id",
        "name",
        "organizations",
        "start_time",
        "classification",
        "in_review",
    ]


class TestLegislationResource(MiscResourceExportTest):
    resource = LegislationResource
    csv_results_count = 6
    json_results_count = 4
    headers = [
        "id",
        "text",
        "epa",
        "passed",
        "classification",
        "timestamp",
        "procedure_phase",
    ]
