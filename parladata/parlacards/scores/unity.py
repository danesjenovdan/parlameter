from datetime import datetime

from django.db.models import Count

from parlacards.models import OrganizationVoteUnity
from parladata.models.ballot import Ballot
from parladata.models.common import Mandate
from parladata.models.memberships import PersonMembership
from parladata.models.organization import Organization
from parladata.models.vote import Vote


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


def get_coalition_member_organizations(coalition, timestamp=None):
    if not timestamp:
        timestamp = datetime.now()

    coalition_members = (
        coalition.organizationmemberships_children.active_at(timestamp)
        .filter(member__classification="pg")
        .values_list("member", flat=True)
    )

    return coalition_members


def calculate_organization_vote_unity(
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

    # annotate ballots with vote options and sort them by count
    # then get the first one which is the most common vote option
    options_aggregated = (
        ballots.values("option")
        .annotate(dcount=Count("option"))
        .order_by("-dcount")
        .first()
    )

    ballots_count = ballots.count()
    if ballots_count == 0:
        return None

    # filter all ballots by the most common vote option and calculate unity
    unity = (
        ballots.filter(option=options_aggregated["option"]).count()
        / ballots_count
        * 100
    )

    return unity


def save_organization_vote_unity(
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
        unity = calculate_organization_vote_unity(
            vote,
            organization,
            playing_field,
            main_playing_field,
            coalition,
        )
        if unity is None:
            continue

        OrganizationVoteUnity(
            organization=organization,
            vote=vote,
            value=unity,
            timestamp=timestamp,
            playing_field=playing_field,
        ).save()


def save_organizations_vote_unities(playing_field, timestamp=None):
    if not timestamp:
        timestamp = datetime.now()

    mandate = Mandate.get_active_mandate_at(timestamp)
    root_organization, main_playing_field = mandate.query_root_organizations(timestamp)
    coalition = get_coalition(main_playing_field, timestamp)

    votes_already_calculated = (
        OrganizationVoteUnity.objects.filter(playing_field=playing_field)
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

        save_organization_vote_unity(
            vote,
            playing_field,
            main_playing_field,
            coalition,
            timestamp,
        )

    print(f"Done: {num}/{num}")


def save_all_organizations_vote_unities(timestamp=None):
    if not timestamp:
        timestamp = datetime.now()

    mandate = Mandate.get_active_mandate_at(timestamp)
    playing_fields = (
        Vote.objects.filter(
            timestamp__lte=timestamp,
            motion__session__mandate=mandate,
        )
        .distinct("motion__session__organizations")
        .values_list("motion__session__organizations", flat=True)
    )
    for playing_field in playing_fields:
        playing_field = Organization.objects.get(id=playing_field)
        print(f"Running votes analyses for: {playing_field.name}")
        save_organizations_vote_unities(playing_field, timestamp)
