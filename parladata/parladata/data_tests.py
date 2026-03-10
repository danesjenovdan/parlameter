from datetime import datetime

from django.conf import settings
from django.contrib.auth.models import Group
from django.db.models import Count

from parlacards.utils import get_playing_fields
from parladata.models import Mandate, Person, Session, Speech, Vote
from parladata.update_utils import send_email


def check_for_duplicated_sessions():
    """
    Test whether there are sessions of the same organization with the same name
    """
    timestamp = datetime.now()
    duplicated_sessions = (
        Session.objects.filter(mandate=2)
        .values("name", "organizations")
        .annotate(same_name=Count("name"))
        .filter(same_name__gt=1)
    )
    return duplicated_sessions


def check_for_duplicated_votes():
    """
    Test whether there are vote with the same name and timestamp
    """
    timestamp = datetime.now()
    pfs = get_playing_fields(timestamp)
    duplicated_votes = (
        Vote.objects.filter(motion__session__organizations__in=pfs)
        .values("name", "timestamp")
        .annotate(same_name=Count("name"))
        .filter(same_name__gt=1)
    )
    return duplicated_votes


def check_num_of_ballots_per_vote():
    """
    Test whether there is a vote where there is no correct number of ballots in relation to the number of voters.
    """
    timestamp = datetime.now()
    pfs = get_playing_fields(timestamp)
    invalid_votes = []
    for pf in pfs:
        vv = Vote.objects.filter(motion__session__organizations=pf).distinct()
        for v in vv:
            number_of_voters = pf.number_of_voters_at(timestamp=v.timestamp)
            count = v.ballots.count()
            if count != number_of_voters:
                invalid_votes.append((v, count, number_of_voters))
    return invalid_votes


def check_for_duplicated_speeches(session_ids=None):
    """
    Test whether there are duplicated speech.
    """
    madnate_id = Mandate.objects.last().id
    if session_ids:
        duplicated_speeches = (
            Speech.objects.filter_valid_speeches()
            .filter(session__mandate=madnate_id, session__id__in=session_ids)
            .values("content", "speaker", "session", "start_time", "order")
            .annotate(same_name=Count("content"))
            .filter(same_name__gt=1)
        )
    else:
        duplicated_speeches = (
            Speech.objects.filter_valid_speeches()
            .filter(session__mandate=madnate_id)
            .values("content", "speaker", "session", "start_time", "order")
            .annotate(same_name=Count("content"))
            .filter(same_name__gt=1)
        )
    return duplicated_speeches


def get_session_with_duplicated_speeches():
    duplicated_speeches = check_for_duplicated_speeches()
    session_ids = set([d["session"] for d in duplicated_speeches])
    return Session.objects.filter(id__in=session_ids)


def run_tests():
    duplicated_sessions = check_for_duplicated_sessions()
    duplicated_votes = check_for_duplicated_votes()
    invalid_ballots = check_num_of_ballots_per_vote()
    sessions_with_duplicated_speeches = get_session_with_duplicated_speeches()

    parser_permission_group = Group.objects.filter(
        name__icontains="parser_owners"
    ).first()

    assert bool(parser_permission_group), "There's no parser owners permission group"

    if (
        duplicated_sessions
        or duplicated_votes
        or invalid_ballots
        or sessions_with_duplicated_speeches
    ):
        for parser_owner in parser_permission_group.user_set.all():
            send_email(
                f"On parlameter {settings.BASE_URL} is some data corruption",
                parser_owner.email,
                "data_validation_email.html",
                {
                    "base_url": settings.BASE_URL,
                    "duplicated_sessions": duplicated_sessions,
                    "duplicated_votes": duplicated_votes,
                    "invalid_ballots": invalid_ballots,
                    "sessions_with_duplicated_speeches": sessions_with_duplicated_speeches,
                },
            )
