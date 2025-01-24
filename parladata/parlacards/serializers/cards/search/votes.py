from parlacards.pagination import create_paginator, create_solr_paginator
from parlacards.serializers.common import CardSerializer, MandateSerializer
from parlacards.serializers.vote import BareVoteSerializer
from parlacards.solr import parse_search_query_params
from parladata.models import Vote


class MandateVotesCardSerializer(CardSerializer):
    def get_results(self, mandate):
        # this is implemented in to_representation for pagination
        return None

    def get_mandate(self, mandate):
        serializer = MandateSerializer(mandate, context=self.context)
        return serializer.data

    def to_representation(self, mandate):
        parent_data = super().to_representation(mandate)

        # this checks if a text parameter was sent in the url
        # if not, it returns all the votes, paged
        if self.context.get("GET", {}).get("text", None):
            solr_params = parse_search_query_params(
                self.context.get("GET", {}), mandate=mandate.id
            )
            paged_object_list, pagination_metadata = create_solr_paginator(
                self.context.get("GET", {}), solr_params, document_type="vote"
            )
        else:
            votes = Vote.objects.filter(
                timestamp__lte=self.context["request_date"],
                motion__session__mandate=mandate,
            ).order_by("-timestamp")
            paged_object_list, pagination_metadata = create_paginator(
                self.context.get("GET", {}), votes
            )

        # serialize votes
        vote_serializer = BareVoteSerializer(
            paged_object_list, many=True, context=self.context
        )

        return {
            **parent_data,
            **pagination_metadata,
            "results": vote_serializer.data,
        }
