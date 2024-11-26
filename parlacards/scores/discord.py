from datetime import datetime

from django.db.models import Count, Max

from parladata.models.vote import Vote
from parladata.models.ballot import Ballot
from parladata.models.common import Mandate
from parladata.models.memberships import PersonMembership
from parladata.models.organization import Organization

from parlacards.models import GroupDiscord, OrganizationVoteDiscord
from parlacards.scores.common import get_dates_between, get_fortnights_between

def calculate_group_discord(group, timestamp=None):
    if not timestamp:
        timestamp = datetime.now()

    mandate = Mandate.get_active_mandate_at(timestamp)

    # get all relevant votes
    votes = Vote.objects.filter(
        timestamp__lte=timestamp,
        motion__session__mandate=mandate
    ).order_by(
        '-timestamp'
    )

    vote_discords = []
    # calculate party_ballots and excluded_vote_ids
    for vote in votes:
        # get relevant voters
        voters = PersonMembership.valid_at(vote.timestamp).filter(
            on_behalf_of=group,
            role='voter'
        )

        ballots = Ballot.objects.filter(
            vote=vote,
            personvoter__in=voters.values_list('member_id', flat=True)
        )

        options_aggregated = ballots.values(
            'option'
        ).annotate(
            dcount=Count('option')
        ).annotate(
            dcount=Count('option')
        ).order_by().aggregate(Max('option'))

        ballots_count = ballots.count()

        if ballots_count > 0:
            vote_discords.append(
                ballots.exclude(
                    option=options_aggregated['option__max']
                ).count() / ballots_count * 100
            )

    if len(vote_discords) == 0:
        return 0

    average_discord = sum(vote_discords) / len(vote_discords)
    return average_discord

def save_group_discord(group, playing_field, timestamp=None):
    if not timestamp:
        timestamp = datetime.now()

    discord = calculate_group_discord(group)

    GroupDiscord(
        group=group,
        value=discord,
        timestamp=timestamp,
        playing_field=playing_field
    ).save()

def save_groups_discords(playing_field, timestamp=None):
    if not timestamp:
        timestamp = datetime.now()

    groups = playing_field.query_parliamentary_groups(timestamp)
    for group in groups:
        save_group_discord(group, playing_field, timestamp)

def save_groups_discords_between(playing_field, datetime_from=None, datetime_to=None):
    if not datetime_from:
        datetime_from = datetime.now()
    if not datetime_to:
        datetime_to = datetime.now()

    for day in get_dates_between(datetime_from, datetime_to):
        save_groups_discords(playing_field, timestamp=day)

def save_sparse_groups_discords_between(playing_field, datetime_from=None, datetime_to=None):
    if not datetime_from:
        datetime_from = datetime.now()
    if not datetime_to:
        datetime_to = datetime.now()

    for day in get_fortnights_between(datetime_from, datetime_to):
        save_groups_discords(playing_field, timestamp=day)


def calculate_organization_vote_discord(vote, organization, playing_field, timestamp=None):
    if not timestamp:
        timestamp = datetime.now()

    # get relevant voters
    if organization == playing_field:
        voters = PersonMembership.valid_at(vote.timestamp).filter(
            organization=organization, role="voter"
        )
    else:
        voters = PersonMembership.valid_at(vote.timestamp).filter(
            on_behalf_of=organization, role="voter"
        )

    ballots = Ballot.objects.filter(
        vote=vote, personvoter__in=voters.values_list("member_id", flat=True)
    )

    options_aggregated = (
        ballots.values("option")
        .annotate(dcount=Count("option"))
        .order_by("-dcount").first()
    )

    ballots_count = ballots.count()
    if ballots_count == 0:
        return None
    discord = (
        ballots.filter(option=options_aggregated["option"]).count()
        / ballots_count
        * 100
    )

    return discord


def save_organization_vote_discord(vote, playing_field, timestamp=None):
    if not timestamp:
        timestamp = datetime.now()

    organizations = playing_field.query_parliamentary_groups(vote.timestamp)
    organizations = organizations.union(Organization.objects.filter(id=playing_field.id))

    for party in organizations:

        discord = calculate_organization_vote_discord(vote, party, playing_field)
        if discord is None:
            continue

        OrganizationVoteDiscord(
            organization=party,
            vote=vote,
            value=discord,
            timestamp=timestamp,
            playing_field=playing_field,
        ).save()


def save_organizations_vote_discords(playing_field, timestamp=None):
    if not timestamp:
        timestamp = datetime.now()

    mandate = Mandate.get_active_mandate_at(timestamp)

    votes_already_calculated = OrganizationVoteDiscord.objects.filter(playing_field=playing_field).values_list('vote__id', flat=True).distinct('vote__id')

    votes = (
        Vote.objects.filter(timestamp__lte=timestamp, motion__session__mandate=mandate)
        .exclude(id__in=votes_already_calculated)
        .exclude(ballots__personvoter__isnull=True)
        .order_by("id").distinct("id")
    )

    for vote in votes:
        save_organization_vote_discord(vote, playing_field, timestamp)

