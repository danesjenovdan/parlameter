from django.db.models import Count

from parlacards.pagination import create_paginator
from parlacards.serializers.common import (
    CardSerializer,
    CommonOrganizationSerializer,
    CommonPersonSerializer,
    MandateSerializer,
)
from parlacards.serializers.vote import BareVoteSerializer
from parladata.models import Ballot, Vote


class ToolsComparatorCardSerializer(CardSerializer):
    def _total_votes(self, playing_field):
        return Vote.objects.filter(
            motion__session__organizations=playing_field,
        ).count()

    def _filter_votes(
        self,
        playing_field,
        same_voters_ids,
        different_voters_ids,
        same_parties_ids,
        different_parties_ids,
    ):
        # TODO: implement same_parties_ids and different_parties_ids

        # We cannot compare votes if there is noone to compare against
        if not same_voters_ids:
            return Vote.objects.none()

        # We cannot compare votes if there are less than two actors
        if len(same_voters_ids + different_voters_ids) < 2:
            return Vote.objects.none()

        # Filter ballots where people from same_voters_ids voted
        same_ballots = Ballot.objects.filter(personvoter__in=same_voters_ids)

        # Find vote_ids where all people from same_voters_ids voted the same
        same_vote_ids = (
            same_ballots.values("vote_id", "option")
            .annotate(voter_count=Count("personvoter"))
            .filter(voter_count=len(same_voters_ids))
            .values("vote_id", "option")
        ).values_list("vote_id", flat=True)

        # Return votes where people from same_voters_ids voted the same if different_voters_ids is None
        same_votes = Vote.objects.filter(
            id__in=same_vote_ids,
            motion__session__organizations=playing_field,
        )
        if not different_voters_ids:
            return same_votes

        # Filter votes where people from same_voters_ids and different_voters_ids voted
        combined_vote_ids = (
            Ballot.objects.filter(
                personvoter__in=different_voters_ids, vote_id__in=same_vote_ids
            )
            .values("vote_id")
            .annotate(voter_count=Count("personvoter"))
            .filter(voter_count=len(different_voters_ids))
            .values_list("vote_id", flat=True)
        )
        combined_ballots = Ballot.objects.filter(
            personvoter__in=same_voters_ids + different_voters_ids,
            vote_id__in=combined_vote_ids,
        )

        # Find ids of votes where people from same_voters_ids votes the same and people from different_voters_ids voted differently
        same_different_votes_ids = (
            combined_ballots.values("vote_id", "option")
            .annotate(voter_count=Count("personvoter"))
            .filter(voter_count=len(same_voters_ids))
            .values("vote_id", "option")
        )

        same_different_votes = same_votes.filter(
            id__in=same_different_votes_ids.values_list("vote_id", flat=True)
        )
        return same_different_votes

    def _groups(self, playing_field, timestamp):
        """Returns serialized parliamentary groups."""
        organizations = playing_field.query_parliamentary_groups(timestamp)
        organization_serializer = CommonOrganizationSerializer(
            organizations,
            context=self.context,
            many=True,
        )
        return organization_serializer.data

    def _members(self, playing_field, timestamp):
        """Returns serialized members."""
        people = playing_field.query_voters(timestamp)
        person_serializer = CommonPersonSerializer(
            people,
            context=self.context,
            many=True,
        )
        return person_serializer.data

    def get_results(self, obj):
        pass

    def get_mandate(self, playing_field):
        organization_membership = playing_field.organization_memberships.filter(
            organization__classification=None
        ).first()
        if organization_membership:
            mandate = organization_membership.mandate
        else:
            mandate = None
        serializer = MandateSerializer(mandate, context=self.context)
        return serializer.data

    def _get_results(self, parent_organization):
        def get_id_list(field_name):
            return list(
                filter(
                    lambda x: x.isdigit(),
                    self.context.get("GET", {}).get(field_name, "").split(","),
                )
            )

        members_same = get_id_list("members_same")
        members_different = get_id_list("members_different")
        groups_same = get_id_list("groups_same")
        groups_different = get_id_list("groups_different")

        return self._filter_votes(
            parent_organization,
            members_same,
            members_different,
            groups_same,
            groups_different,
        )

    def to_representation(self, parent_organization):
        parent_data = super().to_representation(parent_organization)

        votes = self._get_results(parent_organization).order_by("timestamp")

        paged_object_list, pagination_metadata = create_paginator(
            self.context.get("GET", {}), votes, prefix="votes:"
        )

        new_context = dict.copy(self.context)
        new_context["playing_field"] = parent_organization

        # serialize votes
        votes_serializer = BareVoteSerializer(
            paged_object_list, many=True, context=new_context
        )

        return {
            **parent_data,
            **pagination_metadata,
            "results": {
                "groups": self._groups(
                    parent_organization, self.context["request_date"]
                ),
                "members": self._members(
                    parent_organization, self.context["request_date"]
                ),
                "votes": votes_serializer.data,
                "votes_total": self._total_votes(parent_organization),
            },
        }
