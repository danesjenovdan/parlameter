import json

import pytest
from rest_framework.test import APIClient

from export.views import *

client = APIClient()

# testing:
# does endpoint return a successful response (status 200)
# does endpoint return the correct content type
# does response content contain correct fields
# does endpoint return 404 for wrong format or no format
# does endpoint return empty file for non-existing mandate


class ExportTestClass:
    endpoint = ""
    columns = []

    success_get_params = "mandate_id=1"
    fail_get_params = "mandate_id=3"

    no_content = False

    @pytest.mark.django_db()
    def test_export_csv(self):
        response = client.get(f"{self.endpoint}.csv/?{self.success_get_params}")
        # successful response
        assert response.status_code == 200
        # correct response type
        assert response.headers["content-type"] == "text/csv"
        # containts correct fields
        content = response.getvalue()
        lines = content.splitlines()
        columns = lines[0].decode("utf-8").split(",")
        for column in self.columns:
            assert column in columns

    @pytest.mark.django_db()
    def test_export_json(self):
        response = client.get(f"{self.endpoint}.json/?{self.success_get_params}")
        # successful response
        assert response.status_code == 200
        # correct response type
        assert response.headers["content-type"] == "application/json"
        # containts correct fields
        content = json.loads(response.getvalue())
        if self.no_content:
            # empty json has not keys
            return
        json_keys = content[0].keys()
        for column in self.columns:
            assert column in json_keys

    @pytest.mark.django_db()
    def test_export_wrong_format(self):
        response = client.get(f"{self.endpoint}.xslx/?{self.success_get_params}")
        assert response.status_code == 404

    @pytest.mark.django_db()
    def test_export_no_format(self):
        response = client.get(f"{self.endpoint}/?{self.success_get_params}")
        assert response.status_code == 404

    @pytest.mark.django_db()
    def test_export_json_wrong_mandate(self):
        response = client.get(f"{self.endpoint}.json/?{self.fail_get_params}")
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        content = json.loads(response.getvalue())
        assert content == []

    @pytest.mark.django_db()
    def test_export_csv_wrong_mandate(self):
        response = client.get(f"{self.endpoint}.csv/?{self.fail_get_params}")
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv"
        content = response.getvalue()
        lines = content.splitlines()
        assert len(lines) == 2  # colimns and empty line
        columns = lines[0].decode("utf-8").split(",")
        for column in self.columns:
            assert column in columns

    @pytest.mark.django_db()
    def test_export_json_no_mandate(self):
        response = client.get(f"{self.endpoint}.json/")
        assert response.status_code == 400

    @pytest.mark.django_db()
    def test_export_csv_no_mandate(self):
        response = client.get(f"{self.endpoint}.csv/")
        assert response.status_code == 400


# MISC TESTS
class TestMembersView(ExportTestClass):
    endpoint = "/v3/export/misc/members"
    columns = [
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


class TestGroupsView(ExportTestClass):
    endpoint = "/v3/export/misc/groups"
    columns = [
        "id",
        "name",
        "acronym",
        "number_of_members_at",
        "intra_disunion",
        "vocabulary_size",
        "number_of_questions",
        "vote_attendance",
    ]


class TestSessionsView(ExportTestClass):
    endpoint = "/v3/export/misc/sessions"
    columns = [
        "id",
        "name",
        "organizations",
        "start_time",
        "classification",
        "in_review",
    ]


class TestLegislationView(ExportTestClass):
    endpoint = "/v3/export/misc/legislation"
    columns = [
        "id",
        "text",
        "epa",
        "passed",
        "classification",
        "timestamp",
        "procedure_phase",
    ]


# SESSION TESTS
class TestVotesView(ExportTestClass):
    endpoint = "/v3/export/session/votes"
    success_get_params = "mandate_id=1&id=3782"
    fail_get_params = "mandate_id=3&id=1"
    columns = [
        "id",
        "name",
        "motion__text",
        "motion__summary",
        "result",
    ]


class TestSessionsLegislationView(ExportTestClass):
    endpoint = "/v3/export/session/legislation"
    success_get_params = "mandate_id=1&id=3782"
    fail_get_params = "mandate_id=3&id=1"
    columns = [
        "id",
        "text",
        "epa",
        "passed",
        "classification",
        "timestamp",
        "procedure_phase",
    ]


# PERSON TESTS


class PersonCardTest(ExportTestClass):
    """
    Base class for basic person card tests.
    """

    success_get_params = "mandate_id=2&id=245"
    fail_get_params = "mandate_id=3&id=245"
    columns = ["name", "value", "timestamp"]


class TestPersonVocabularySizeView(PersonCardTest):
    endpoint = "/v3/export/person/vocabulary-size"


class TestPersonInfoView(PersonCardTest):
    endpoint = "/v3/export/person/basic-information"
    columns = [
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


class TestPersonVotesView(PersonCardTest):
    endpoint = "/v3/export/person/votes"
    columns = ["name", "vote_text", "option", "timestamp", "passed"]


class TestPersonQuestionsView(PersonCardTest):
    endpoint = "/v3/export/person/questions"
    columns = [
        "authors",
        "title",
        "type_of_question",
        "recipient_people",
        "recipient_text",
        "timestamp",
    ]
    no_content = True


class TestPersonMembershipsView(PersonCardTest):
    endpoint = "/v3/export/person/memberships"
    columns = [
        "name",
        "role",
        "organization",
        "on_behalf_of",
        "start_time",
        "end_time",
        "mandate",
    ]


class TestPersonVotesInCommonView(PersonCardTest):
    endpoint = "/v3/export/person/most-votes-in-common"
    columns = ["name", "distance_with", "value", "timestamp"]


class TestPersonDeviationFromGroupView(PersonCardTest):
    endpoint = "/v3/export/person/deviation-from-group"


class TestPersonAverageNumberOfSpeechesPerSessionView(PersonCardTest):
    endpoint = "/v3/export/person/average-number-of-speeches-per-session"


class TestPersonNumberOfQuestionsView(PersonCardTest):
    endpoint = "/v3/export/person/number-of-questions"


class TestPersonVoteAttendanceView(PersonCardTest):
    endpoint = "/v3/export/person/vote-attendance"


class TestPersonMonthlyVoteAttendanceView(PersonCardTest):
    endpoint = "/v3/export/person/monthly-vote-attendance"


class TestPersonNumberOfSpokenWordsView(PersonCardTest):
    endpoint = "/v3/export/person/number-of-spoken-words"


class TestPersonTfidfView(PersonCardTest):
    endpoint = "/v3/export/person/tfidf"
    columns = ["name", "value", "token", "timestamp"]
    no_content = True


class TestPersonStyleScoreView(PersonCardTest):
    endpoint = "/v3/export/person/style-scores"
    columns = ["name", "style", "value", "timestamp"]
    no_content = True


# GROUP TESTS
