from datetime import datetime

from django.db.models import Count, Max

from parlacards.models import GroupDiscord, OrganizationVoteDiscord
from parlacards.scores.common import get_dates_between, get_fortnights_between
from parladata.models.ballot import Ballot
from parladata.models.common import Mandate
from parladata.models.memberships import PersonMembership
from parladata.models.organization import Organization
from parladata.models.vote import Vote


def calculate_group_discord(group, timestamp=None):
    if not timestamp:
        timestamp = datetime.now()

    mandate = Mandate.get_active_mandate_at(timestamp)

    # get all relevant votes
    votes = Vote.objects.filter(
        timestamp__lte=timestamp, motion__session__mandate=mandate
    ).order_by("-timestamp")

    vote_discords = []
    # calculate party_ballots and excluded_vote_ids
    for vote in votes:
        # get relevant voters
        voters = PersonMembership.valid_at(vote.timestamp).filter(
            on_behalf_of=group, role="voter"
        )

        ballots = Ballot.objects.filter(
            vote=vote, personvoter__in=voters.values_list("member_id", flat=True)
        )

        options_aggregated = (
            ballots.values("option")
            .annotate(dcount=Count("option"))
            .annotate(dcount=Count("option"))
            .order_by()
            .aggregate(Max("option"))
        )

        ballots_count = ballots.count()

        if ballots_count > 0:
            vote_discords.append(
                ballots.exclude(option=options_aggregated["option__max"]).count()
                / ballots_count
                * 100
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
        group=group, value=discord, timestamp=timestamp, playing_field=playing_field
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


def save_sparse_groups_discords_between(
    playing_field, datetime_from=None, datetime_to=None
):
    if not datetime_from:
        datetime_from = datetime.now()
    if not datetime_to:
        datetime_to = datetime.now()

    for day in get_fortnights_between(datetime_from, datetime_to):
        save_groups_discords(playing_field, timestamp=day)


def calculate_organization_vote_discord(
    vote,
    organization,
    playing_field,
    main_playing_field,
    coalition,
):
    # get relevant voters
    if organization == main_playing_field:
        # if organization is parliament/municipality then get all voters
        voter_memberships = PersonMembership.valid_at(vote.timestamp).filter(
            role="voter",
            organization=main_playing_field,
        )
    elif organization == coalition:
        # if organization is coalition then get all voters from coalition
        organizations = get_coalition_member_organizations(coalition, vote.timestamp)
        voter_memberships = PersonMembership.valid_at(vote.timestamp).filter(
            role="voter",
            organization=main_playing_field,
            on_behalf_of__in=organizations,
        )
    else:
        # in this case organization is a parliamentary group, but because
        # on_behalf_of is not always set on other voter memberships we use
        # main_playing_field to get voters from specific groups, they will be
        # filtered by ballots later anyway
        voter_memberships = PersonMembership.valid_at(vote.timestamp).filter(
            role="voter",
            organization=main_playing_field,
            on_behalf_of=organization,
        )

    voters = voter_memberships.values_list("member_id", flat=True)

    ballots = Ballot.objects.filter(
        vote=vote,
        personvoter__in=voters,
    )

    options_aggregated = (
        ballots.values("option")
        .annotate(dcount=Count("option"))
        .order_by("-dcount")
        .first()
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


def save_organization_vote_discord(
    vote,
    playing_field,
    main_playing_field,
    coalition,
    timestamp=None,
):
    if not timestamp:
        timestamp = datetime.now()

    organizations = [main_playing_field]

    if coalition:
        organizations.append(coalition)

    if playing_field.classification == "root":
        organizations += list(playing_field.query_parliamentary_groups(vote.timestamp))
    else:
        organizations += list(playing_field.query_voter_groups(vote.timestamp))

    for organization in organizations:
        discord = calculate_organization_vote_discord(
            vote,
            organization,
            playing_field,
            main_playing_field,
            coalition,
        )
        if discord is None:
            continue

        OrganizationVoteDiscord(
            organization=organization,
            vote=vote,
            value=discord,
            timestamp=timestamp,
            playing_field=playing_field,
        ).save()


def get_coalition_member_organizations(coalition, timestamp=None):
    if not timestamp:
        timestamp = datetime.now()

    coalition_members = (
        coalition.organizationmemberships_children.active_at(timestamp)
        .filter(member__classification="pg")
        .values_list("member", flat=True)
    )

    return coalition_members


def get_coalition(main_playing_field, timestamp=None):
    if not timestamp:
        timestamp = datetime.now()

    coalition_organization_membership = (
        main_playing_field.organizationmemberships_children.active_at(timestamp)
        .filter(member__classification="coalition")
        .first()
    )

    if not coalition_organization_membership:
        return None

    return coalition_organization_membership.member


def save_organizations_vote_discords(playing_field, timestamp=None):
    if not timestamp:
        timestamp = datetime.now()

    mandate = Mandate.get_active_mandate_at(timestamp)
    root_organization, main_playing_field = mandate.query_root_organizations(timestamp)
    coalition = get_coalition(main_playing_field, timestamp)

    votes_already_calculated = (
        OrganizationVoteDiscord.objects.filter(playing_field=playing_field)
        .values_list("vote__id", flat=True)
        .distinct("vote__id")
    )

    votes = (
        Vote.objects.filter(
            timestamp__lte=timestamp,
            motion__session__mandate=mandate,
            motion__session__organizations=playing_field,
        )
        .exclude(id__in=votes_already_calculated)
        .exclude(ballots__personvoter__isnull=True)
        .order_by("id")
        .distinct("id")
    )

    i = 0
    num = len(votes)

    for vote in votes:
        i += 1
        if i % 100 == 0:
            print(f"Progress: {i}/{num}")

        save_organization_vote_discord(
            vote,
            playing_field,
            main_playing_field,
            coalition,
            timestamp,
        )

    print(f"Done: {num}/{num}")
