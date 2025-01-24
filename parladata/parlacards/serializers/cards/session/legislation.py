from parlacards.pagination import create_paginator
from parlacards.serializers.cards.misc.legislation import LegislationMixin
from parlacards.serializers.common import CardSerializer, MandateSerializer
from parlacards.serializers.legislation import LegislationSerializer


class SessionLegislationCardSerializer(CardSerializer, LegislationMixin):
    def get_results(self, session):
        # this is implemented in to_representation for pagination
        return None

    def get_mandate(self, session):
        serializer = MandateSerializer(session.mandate, context=self.context)
        return serializer.data

    def to_representation(self, session):
        parent_data = super().to_representation(session)

        legislation = self._get_legislation(
            self.context.get("GET", {}), session=session
        )

        paged_object_list, pagination_metadata = create_paginator(
            self.context.get("GET", {}), legislation, prefix="legislation:"
        )

        legislation_serializer = LegislationSerializer(
            paged_object_list, many=True, context=self.context
        )

        # TODO standardize this and more importantly, cache it!
        classifications = self._get_classifications()
        statuses = self._get_statuses()

        return {
            **parent_data,
            **pagination_metadata,
            "results": {
                "legislation": legislation_serializer.data,
                "classifications": classifications,
                "statuses": statuses,
            },
        }
