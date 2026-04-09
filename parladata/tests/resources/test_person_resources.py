import json

import pytest

from export.resources.person import *
from tests.fixtures.common import *


class PersonResourceExportTest:
    resource = None
    headers = ["name", "value", "timestamp"]
    csv_results_count = 3
    json_results_count = 1

    @pytest.mark.django_db()
    def test_export_as_generator_json(self, first_mandate, first_person):
        resource = self.resource()
        generator = resource.export_as_generator_json(
            mandate_id=first_mandate.id, request_id=first_person.id
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
    def test_export_as_generator_csv(self, first_mandate, first_person):
        resource = self.resource()
        generator = resource.export_as_generator_csv(
            mandate_id=first_mandate.id, request_id=first_person.id
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


class TestPersonInfoCardExportResource(PersonResourceExportTest):
    resource = PersonInfoCardResource
    headers = [
        "name",
        "date_of_birth",
        "image",
        "education",
        "education_level",
        "previous_occupation",
        "number_of_mandates",
        "number_of_voters",
        "parliamentary_group",
    ]


class TestPersonNumberOfSpokenWordsResource(PersonResourceExportTest):
    resource = PersonNumberOfSpokenWordsResource


class TestVocabularySizeResource(PersonResourceExportTest):
    resource = VocabularySizeResource


class TestAgreementWithGroupResource(PersonResourceExportTest):
    resource = AgreementWithGroupResource


class TestPersonMonthlyVoteAttendanceResource(PersonResourceExportTest):
    resource = PersonMonthlyVoteAttendanceResource
    csv_results_count = 4
    json_results_count = 2


class TestPersonVoteAttendanceResource(PersonResourceExportTest):
    resource = PersonVoteAttendanceResource


class TestPersonStyleScoresResource(PersonResourceExportTest):
    resource = PersonStyleScoresResource
    csv_results_count = 2
    json_results_count = 0


class TestPersonAvgSpeechesPerSessionResource(PersonResourceExportTest):
    resource = PersonAvgSpeechesPerSessionResource


class TestVotingDistanceResource(PersonResourceExportTest):
    resource = VotingDistanceResource
    headers = ["name", "distance_with", "value", "timestamp"]
    csv_results_count = 46
    json_results_count = 44


class TestPersonNumberOfQuestionsResource(PersonResourceExportTest):
    resource = PersonNumberOfQuestionsResource


class TestPersonPublicQuestionsResource(PersonResourceExportTest):
    resource = PersonPublicQuestionsResource
    headers = ["name", "created_at", "approved_at", "text", "answer_text", "answer_at"]
    csv_results_count = 2
    json_results_count = 0


class TestPersonTfidfResource(PersonResourceExportTest):
    resource = PersonTfidfResource
    headers = ["name", "value", "token", "timestamp"]
    csv_results_count = 2
    json_results_count = 0


class TestPersonMembershipResource(PersonResourceExportTest):
    resource = PersonMembershipResource
    headers = [
        "name",
        "role",
        "organization",
        "on_behalf_of",
        "start_time",
        "end_time",
        "mandate",
    ]
    csv_results_count = 5
    json_results_count = 3


class TestPersonBallotsResource(PersonResourceExportTest):
    resource = PersonBallotsResource
    headers = ["name", "vote_text", "option", "timestamp", "passed"]
    csv_results_count = 42
    json_results_count = 40


class TestPersonQuestionsResource(PersonResourceExportTest):
    resource = PersonQuestionsResource
    headers = [
        "authors",
        "title",
        "type_of_question",
        "recipient_people",
        "recipient_text",
        "timestamp",
    ]
    csv_results_count = 2
    json_results_count = 0
