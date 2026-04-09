from datetime import datetime

import pytest
from rest_framework.test import APIClient

from parlacards.views import *
from tests.fixtures.common import *

client = APIClient()


def single_test_url(url, params, status_code=200):
    response = client.get(url, params)
    assert response.status_code == status_code


def run_test_urls(url, fixtures):
    for fixture in fixtures:
        single_test_url(url, fixture)


def run_test_for_bicameral_system(url, result_length, params_1, params_2):
    response2 = client.get(url, params_1)
    response1 = client.get(url, params_2)
    assert response1.status_code == 200
    assert response2.status_code == 200
    assert len(response1.json().get("results", [])) == result_length
    assert len(response2.json().get("results", [])) == result_length


# tests
@pytest.mark.django_db()
def test_misc_members():
    response = client.get(
        "/v3/cards/misc/members/?id=1&members:per_page=10&members:page=1&text=&order_by=name&preferred_pronoun=she"
    )
    assert response.status_code == 200


@pytest.mark.django_db()
def test_misc_groups(current_root_org, first_root_org):
    run_test_urls("/v3/cards/misc/groups/", [first_root_org, current_root_org])


@pytest.mark.django_db()
def test_misc_sessions(first_mandate_params, current_mandate_params):
    run_test_urls(
        "/v3/cards/misc/sessions/", [first_mandate_params, current_mandate_params]
    )


@pytest.mark.django_db()
def test_misc_legislation(first_mandate_params, current_mandate_params):
    run_test_urls(
        "/v3/cards/misc/legislation/", [first_mandate_params, current_mandate_params]
    )


@pytest.mark.django_db()
def test_misc_last_session(first_root_org, current_root_org):
    run_test_urls("/v3/cards/misc/last-session/", [first_root_org, current_root_org])


@pytest.mark.django_db()
def test_misc_search(first_mandate_params, current_mandate_params):
    run_test_urls(
        "/v3/cards/misc/search/", [first_mandate_params, current_mandate_params]
    )


@pytest.mark.django_db()
def test_misc_menu_search(first_mandate_params, current_mandate_params):
    run_test_urls(
        "/v3/cards/misc/menu-search/", [first_mandate_params, current_mandate_params]
    )


@pytest.mark.django_db()
def test_misc_basic_information(first_mandate_params, current_mandate_params):
    run_test_urls(
        "/v3/cards/misc/basic-information/",
        [first_mandate_params, current_mandate_params],
    )


@pytest.mark.django_db()
def test_person_basic_information(first_mandate_member, all_mandate_member):
    run_test_urls(
        "/v3/cards/person/basic-information/",
        [first_mandate_member, all_mandate_member],
    )


@pytest.mark.django_db()
def test_person_vocabulary_size(first_mandate_member, all_mandate_member):
    run_test_urls(
        "/v3/cards/person/vocabulary-size/", [first_mandate_member, all_mandate_member]
    )


@pytest.mark.django_db()
def test_person_votes(first_mandate_member, all_mandate_member):
    run_test_urls("/v3/cards/person/votes/", [first_mandate_member, all_mandate_member])


@pytest.mark.django_db()
def test_person_questions(first_mandate_member, all_mandate_member):
    run_test_urls(
        "/v3/cards/person/questions/", [first_mandate_member, all_mandate_member]
    )
    # TODO we should also test the questions aren't all the same


@pytest.mark.django_db()
def test_person_memberships(first_mandate_member, all_mandate_member):
    run_test_urls(
        "/v3/cards/person/memberships/", [first_mandate_member, all_mandate_member]
    )


@pytest.mark.django_db()
def test_person_most_votes_in_common(first_mandate_member, all_mandate_member):
    run_test_urls(
        "/v3/cards/person/most-votes-in-common/",
        [first_mandate_member, all_mandate_member],
    )


@pytest.mark.django_db()
def test_person_least_votes_in_common(first_mandate_member, all_mandate_member):
    run_test_urls(
        "/v3/cards/person/least-votes-in-common/",
        [first_mandate_member, all_mandate_member],
    )


@pytest.mark.django_db()
def test_person_least_votes_in_common_for_bicameral_systems(
    bicameral_person_1, bicameral_person_2
):
    run_test_for_bicameral_system(
        "/v3/cards/person/least-votes-in-common/",
        5,
        bicameral_person_1,
        bicameral_person_2,
    )


@pytest.mark.django_db()
def test_person_most_votes_in_common_for_bicameral_systems(
    bicameral_person_1, bicameral_person_2
):
    run_test_for_bicameral_system(
        "/v3/cards/person/most-votes-in-common/",
        5,
        bicameral_person_1,
        bicameral_person_2,
    )


@pytest.mark.django_db()
def test_person_agreement_with_group(first_mandate_member, all_mandate_member):
    run_test_urls(
        "/v3/cards/person/agreement-with-group/",
        [first_mandate_member, all_mandate_member],
    )


@pytest.mark.django_db()
def test_person_average_number_of_speeches_per_session(
    first_mandate_member, all_mandate_member
):
    run_test_urls(
        "/v3/cards/person/average-number-of-speeches-per-session/",
        [first_mandate_member, all_mandate_member],
    )


@pytest.mark.django_db()
def test_person_questions(first_mandate_member, all_mandate_member):
    run_test_urls(
        "/v3/cards/person/number-of-questions/",
        [first_mandate_member, all_mandate_member],
    )


@pytest.mark.django_db()
def test_person_vote_attendance(first_mandate_member, all_mandate_member):
    run_test_urls(
        "/v3/cards/person/vote-attendance/", [first_mandate_member, all_mandate_member]
    )


@pytest.mark.django_db()
def test_person_recent_activity(first_mandate_member, all_mandate_member):
    run_test_urls(
        "/v3/cards/person/recent-activity/", [first_mandate_member, all_mandate_member]
    )


@pytest.mark.django_db()
def test_person_monthly_vote_attendance(first_mandate_member, all_mandate_member):
    run_test_urls(
        "/v3/cards/person/monthly-vote-attendance/",
        [first_mandate_member, all_mandate_member],
    )


@pytest.mark.django_db()
def test_person_monthly_vote_attendance_for_bicameral_systems(
    bicameral_person_1, bicameral_person_2
):
    run_test_for_bicameral_system(
        "/v3/cards/person/monthly-vote-attendance/",
        1,
        bicameral_person_1,
        bicameral_person_2,
    )


@pytest.mark.django_db()
def test_person_style_scores(first_mandate_member, all_mandate_member):
    run_test_urls(
        "/v3/cards/person/style-scores/", [first_mandate_member, all_mandate_member]
    )


@pytest.mark.django_db()
def test_person_number_of_spoken_words(first_mandate_member, all_mandate_member):
    run_test_urls(
        "/v3/cards/person/number-of-spoken-words/",
        [first_mandate_member, all_mandate_member],
    )


@pytest.mark.django_db()
def test_person_tfidf(first_mandate_member, all_mandate_member):
    run_test_urls("/v3/cards/person/tfidf/", [first_mandate_member, all_mandate_member])


@pytest.mark.django_db()
def test_person_media_reports(first_mandate_member, all_mandate_member):
    run_test_urls(
        "/v3/cards/person/media-reports/", [first_mandate_member, all_mandate_member]
    )


# TODO: needs settings.SOLR_URL
# @pytest.mark.django_db()
# def test_person_speeches():
#     response = client.get('/v3/cards/person/speeches/?id=19')
#     assert response.status_code == 200


@pytest.mark.django_db()
def test_group_basic_information(first_mandate_party, all_mandate_party):
    run_test_urls(
        "/v3/cards/group/basic-information/", [first_mandate_party, all_mandate_party]
    )


@pytest.mark.django_db()
def test_group_members(first_mandate_party, all_mandate_party):
    run_test_urls("/v3/cards/group/members/", [first_mandate_party, all_mandate_party])


@pytest.mark.django_db()
def test_group_vocabulary_size(first_mandate_party, all_mandate_party):
    run_test_urls(
        "/v3/cards/group/vocabulary-size/", [first_mandate_party, all_mandate_party]
    )


@pytest.mark.django_db()
def test_group_number_of_questions(first_mandate_party, all_mandate_party):
    run_test_urls(
        "/v3/cards/group/number-of-questions/", [first_mandate_party, all_mandate_party]
    )


@pytest.mark.django_db()
def test_group_monthly_vote_attendance(first_mandate_party, all_mandate_party):
    run_test_urls(
        "/v3/cards/group/monthly-vote-attendance/",
        [first_mandate_party, all_mandate_party],
    )


@pytest.mark.django_db()
def test_group_monthly_vote_attendance_for_bicameral_systems(
    bicameral_org_1, bicameral_org_2
):
    run_test_for_bicameral_system(
        "/v3/cards/group/monthly-vote-attendance/", 1, bicameral_org_1, bicameral_org_2
    )


@pytest.mark.django_db()
def test_group_questions(first_mandate_party, all_mandate_party):
    run_test_urls(
        "/v3/cards/group/questions/", [first_mandate_party, all_mandate_party]
    )
    # TODO we should also test the questions aren't all the same


@pytest.mark.django_db()
def test_group_vote_attendance(first_mandate_party, all_mandate_party):
    run_test_urls(
        "/v3/cards/group/vote-attendance/", [first_mandate_party, all_mandate_party]
    )


@pytest.mark.django_db()
def test_group_votes(first_mandate_party, all_mandate_party):
    run_test_urls("/v3/cards/group/votes/", [first_mandate_party, all_mandate_party])


@pytest.mark.django_db()
def test_group_most_votes_in_common(first_mandate_party, all_mandate_party):
    run_test_urls(
        "/v3/cards/group/most-votes-in-common/",
        [first_mandate_party, all_mandate_party],
    )


@pytest.mark.django_db()
def test_group_least_votes_in_common(first_mandate_party, all_mandate_party):
    run_test_urls(
        "/v3/cards/group/least-votes-in-common/",
        [first_mandate_party, all_mandate_party],
    )


@pytest.mark.django_db()
def test_group_agreement_with_group(first_mandate_party, all_mandate_party):
    run_test_urls(
        "/v3/cards/group/agreement-with-group/",
        [first_mandate_party, all_mandate_party],
    )


@pytest.mark.django_db()
def test_group_tfidf(first_mandate_party, all_mandate_party):
    run_test_urls("/v3/cards/group/tfidf/", [first_mandate_party, all_mandate_party])


@pytest.mark.django_db()
def test_group_style_scores(first_mandate_party, all_mandate_party):
    run_test_urls(
        "/v3/cards/group/style-scores/", [first_mandate_party, all_mandate_party]
    )


@pytest.mark.django_db()
def test_group_unity(first_mandate_party, all_mandate_party):
    run_test_urls("/v3/cards/group/unity/", [first_mandate_party, all_mandate_party])


@pytest.mark.django_db()
def test_group_unity_with_nonexistent_id():
    response = client.get("/v3/cards/group/unity/?id=12000")
    assert response.status_code == 404


@pytest.mark.django_db()
def test_group_media_reports():
    response = client.get("/v3/cards/group/media-reports/?id=19")
    assert response.status_code == 200


# TODO: needs settings.SOLR_URL
# @pytest.mark.django_db()
# def test_group_speeches():
#     response = client.get('/v3/cards/group/speeches/?id=19')
#     assert response.status_code == 200


@pytest.mark.django_db()
def test_session_legislation():
    response = client.get("/v3/cards/session/legislation/?id=3782")
    assert response.status_code == 200


@pytest.mark.django_db()
def test_session_speeches():
    response = client.get("/v3/cards/session/speeches/?id=3782")
    assert response.status_code == 200


@pytest.mark.django_db()
def test_session_votes():
    response = client.get("/v3/cards/session/votes/?id=3782")
    assert response.status_code == 200


@pytest.mark.django_db()
def test_session_votes():
    response = client.get("/v3/cards/session/tfidf/?id=3782")
    assert response.status_code == 200


@pytest.mark.django_db()
def test_single_speech():
    response = client.get("/v3/cards/speech/single/?id=68974")
    assert response.status_code == 200


@pytest.mark.django_db()
def test_single_vote():
    response = client.get("/v3/cards/vote/single/?id=10229")
    assert response.status_code == 200


@pytest.mark.django_db()
def test_single_vote_with_only_anonymous_ballots():
    response = client.get("/v3/cards/vote/single/?id=10229")
    assert response.status_code == 200


@pytest.mark.django_db()
def test_single_vote_with_some_anonymous_ballots():
    response = client.get("/v3/cards/vote/single/?id=10229")
    assert response.status_code == 200


@pytest.mark.django_db()
def test_single_vote_without_ballots():
    response = client.get("/v3/cards/vote/single/?id=10229")
    assert response.status_code == 200


@pytest.mark.django_db()
def test_single_session():
    response = client.get("/v3/cards/session/single/?id=3782")
    assert response.status_code == 200


@pytest.mark.django_db()
def test_session_agenda_items():
    response = client.get("/v3/cards/session/agenda-items/?id=3782")
    assert response.status_code == 200


@pytest.mark.django_db()
def test_session_minutes():
    response = client.get("/v3/cards/session/minutes/?id=3782")
    assert response.status_code == 200


@pytest.mark.django_db()
def test_single_law():
    response = client.get("/v3/cards/legislation/single/?id=1403")
    assert response.status_code == 200


@pytest.mark.django_db()
def test_single_minutes():
    response = client.get("/v3/cards/minutes/single/?id=28813")
    assert response.status_code == 200


# TODO: needs settings.SOLR_URL
# @pytest.mark.django_db()
# def test_search_speeches():
#     response = client.get('/v3/cards/search/speeches/?id=1')
#     assert response.status_code == 200

# TODO: needs settings.SOLR_URL
# @pytest.mark.django_db()
# def test_search_most_used_by_people():
#     response = client.get('/v3/cards/search/most-used-by-people/?id=1')
#     assert response.status_code == 200

# TODO: needs settings.SOLR_URL
# @pytest.mark.django_db()
# def test_search_usage_by_group():
#     response = client.get('/v3/cards/search/usage-by-group/?id=1')
#     assert response.status_code == 200

# TODO: needs settings.SOLR_URL
# @pytest.mark.django_db()
# def test_search_usage_through_time():
#     response = client.get('/v3/cards/search/usage-through-time/?id=1')
#     assert response.status_code == 200


@pytest.mark.django_db()
def test_search_votes():
    response = client.get("/v3/cards/search/votes/?id=1")
    assert response.status_code == 200


@pytest.mark.django_db()
def test_search_legislation():
    response = client.get("/v3/cards/search/legislation/?id=1")
    assert response.status_code == 200


@pytest.mark.django_db()
def test_create_and_get_quote():
    response = client.post(
        "/v3/cards/speech/quote/",
        {"speech": 68974, "start_index": 6, "end_index": 9, "quote_content": "dan"},
    )
    assert response.status_code == 201

    response = client.get("/v3/cards/speech/quote/?id=1")
    assert response.status_code == 200


@pytest.mark.django_db()
def test_public_person_question():
    response = client.post(
        "/v3/cards/person/public-questions/?id=240",
        {
            "recaptcha": "token",
            "author_email": "ivan@email.com",
            "text": "what what what",
            "recipient_person": 240,
        },
    )
    assert response.status_code == 201

    response = client.get("/v3/cards/person/public-questions/?id=240")
    assert response.status_code == 200
    # new question is not approved
    assert len(response.json()["results"]) == 0


@pytest.mark.django_db()
def test_validation_error_on_create_quote():
    response = client.post(
        "/v3/cards/speech/quote/",
        {"speech": 68974, "start_index": 6, "end_index": 10, "quote_content": "ivan"},
    )
    assert response.status_code == 400
    assert "quote_content" in response.json().keys()
