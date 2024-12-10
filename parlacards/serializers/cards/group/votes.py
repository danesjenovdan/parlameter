from django.db.models import Max
from rest_framework.exceptions import NotFound

from parlacards.pagination import create_paginator
from parlacards.serializers.ballot import BallotSerializer
from parlacards.serializers.common import GroupScoreCardSerializer
from parlacards.serializers.vote import VoteSerializer
from parladata.models.ballot import Ballot
from parladata.models.common import Mandate
from parladata.models.memberships import PersonMembership
from parladata.models.vote import Vote


class GroupVoteCardSerializer(GroupScoreCardSerializer):
    def get_results(self, group):
        # this is implemented in to_representation for pagination
        return None

    def to_representation(self, group):
        parent_data = super().to_representation(group)

        # get active madnate from timestamp and it's begining and ending/current timestamp
        root_organization_membership = group.query_root_organization_on_date(
            self.context["request_date"]
        )

        if root_organization_membership:
            # group is active in mandate on current date.
            mandate = Mandate.get_active_mandate_at(self.context["request_date"])
            root_organization = root_organization_membership.organization
        else:
            # TODO reconsider if this is necessary or if we should just raise exception

            # get last active mandate for organization which has not active membership on current mandate
            organization_membership = group.organization_memberships.latest("end_time")
            # organization membership has end time for last mandate
            if not organization_membership.end_time:
                msg = f'Organization {organization_membership.member.name} has not membership on requested date {self.context["request_date"]}!'
                raise NotFound(detail=msg, code=404)

            mandate = Mandate.get_active_mandate_at(organization_membership.end_time)
            root_organization = organization_membership.organization

        from_timestamp, to_timestamp = mandate.get_time_range_from_mandate(
            self.context["request_date"]
        )

        votes = Vote.objects.filter(
            timestamp__range=(from_timestamp, to_timestamp),
            motion__session__organizations=root_organization,
        ).order_by(
            "-timestamp", "-id"  # fallback ordering
        )

        # TODO: maybe lemmatize?, maybe search by each word separately?
        if text := self.context.get("GET", {}).get("text", None):
            votes = votes.filter(motion__text__icontains=text)

        paged_object_list, pagination_metadata = create_paginator(
            self.context.get("GET", {}), votes, prefix="ballots:"
        )

        party_ballots = []
        for vote in paged_object_list:
            voter_ids = (
                PersonMembership.valid_at(vote.timestamp)
                .filter(on_behalf_of=group, role="voter")
                .values_list("member_id", flat=True)
            )

            # TODO this is very similar to
            # parlacards.scores.devaition_from_group.get_group_ballot
            # consider refactoring one or both
            # the difference is that this function needs all the ballots
            ballots = Ballot.objects.filter(vote=vote, personvoter__in=voter_ids)

            # if there are no ballots max option will be None
            options_aggregated = ballots.values("option").aggregate(Max("option"))

            # this is a in memory only ballot object that is only constructed
            # for the serializer to use
            fake_ballot = Ballot(
                option=options_aggregated["option__max"],
                vote=vote,
            )

            # always append a ballot to party_ballots so that pagination returns
            # an expected number of objects, even if option is None
            party_ballots.append(fake_ballot)

        # serialize ballots
        ballot_serializer = BallotSerializer(
            party_ballots, many=True, context=self.context
        )

        return {
            **parent_data,
            **pagination_metadata,
            "results": {
                "ballots": ballot_serializer.data,
            },
        }
