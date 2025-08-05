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


class VoteComparatorCardSerializer(CardSerializer):
    def _filter_votes(self, same_voters_ids, different_voters_ids=None):
        if same_voters_ids is not None:
            same_voters_ids = same_voters_ids.split(",")

        if different_voters_ids is not None:
            different_voters_ids = different_voters_ids.split(",")

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
        same_votes = Vote.objects.filter(id__in=same_vote_ids)
        if different_voters_ids is None:
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
        ).order_by("timestamp")
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

    def _get_results(self):
        people_same = self.context.get("GET", {}).get("people_same", None)
        people_different = self.context.get("GET", {}).get("people_different", None)
        parties_same = self.context.get("GET", {}).get("parties_same", None)
        parties_different = self.context.get("GET", {}).get("parties_different", None)

        # TODO: implement parties_same and parties_different

        return self._filter_votes(people_same, people_different)

    def to_representation(self, parent_organization):
        parent_data = super().to_representation(parent_organization)

        votes = self._get_results().order_by("timestamp")

        paged_object_list, pagination_metadata = create_paginator(
            self.context.get("GET", {}), votes, prefix="comparator:"
        )

        new_context = dict.copy(self.context)
        new_context["playing_field"] = parent_organization

        # serialize people
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
            },
        }
