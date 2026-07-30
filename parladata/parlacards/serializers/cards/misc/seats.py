from django.db.models import Q
from rest_framework import serializers

from parlacards.serializers.cards.misc.groups import MiscGroupsCardSerializer
from parlacards.serializers.common import (
    CommonOrganizationSerializer,
    CommonPersonSerializer,
)
from parladata.models.memberships import PersonMembership


class MinimalPersonSerializer(CommonPersonSerializer):
    def calculate_cache_key(self, person):
        organization = person.parliamentary_group_on_date(self.context["request_date"])

        if organization:
            timestamp = max([person.updated_at, organization.updated_at])
        else:
            timestamp = person.updated_at

        return f'MinimalPersonSerializer_{person.id}_{self.context["request_date"].isoformat()}_{timestamp.isoformat()}'

    # disable some fields from the parent serializer
    group = None
    image = None
    is_active = None


class GroupSeatsSerializer(CommonOrganizationSerializer):
    def calculate_cache_key(self, group):
        last_membership = PersonMembership.objects.filter(
            Q(organization=group) | Q(on_behalf_of=group)
        ).latest("updated_at")

        timestamp = max([group.updated_at, last_membership.updated_at])

        playing_field = self.context["playing_field"]

        return f"GroupSeatsSerializer_{group.id}_{playing_field.id}_{timestamp.isoformat()}"

    def get_results(self, obj):
        seat_count = obj.number_of_members_at(self.context["request_date"])
        members = obj.query_members(timestamp=self.context["request_date"]).order_by(
            "latest_name", "id"
        )
        members_serializer = MinimalPersonSerializer(
            members, many=True, context=self.context
        )

        return {
            "seat_count": seat_count,
            "members": members_serializer.data,
        }

    results = serializers.SerializerMethodField()


class MiscSeatsCardSerializer(MiscGroupsCardSerializer):
    def get_results(self, parent_organization):
        new_context = dict.copy(self.context)
        new_context["playing_field"] = parent_organization

        serializer = GroupSeatsSerializer(
            parent_organization.query_parliamentary_groups(
                self.context["request_date"]
            ),
            many=True,
            context=new_context,
        )
        return serializer.data
