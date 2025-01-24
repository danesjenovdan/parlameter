from rest_framework import serializers

from parlacards.serializers.common import (
    CommonCachableSerializer,
    CommonPersonSerializer,
    CommonSerializer,
    VersionableSerializerField,
)
from parladata.models.link import Link


class OrganizationBasicInfoSerializer(CommonCachableSerializer):
    def calculate_cache_key(self, instance):
        try:
            last_membership_updated_at = instance.personmemberships_children.latest(
                "updated_at"
            ).updated_at
            cache_date = max([last_membership_updated_at, instance.updated_at])
        except:
            # if there is organization without memberships
            cache_date = instance.updated_at
        return f'OrganizationBasicInfoSerializer_{instance.id}_{self.context["request_date"].strftime("%Y-%m-%dT%H:%M:%S")}_{cache_date.strftime("%Y-%m-%dT%H:%M:%S")}'

    # TODO this will return all links they
    # should be filtered to only contain
    # social networks
    def get_social_networks(self, obj):
        links = Link.objects.filter(organization=obj)
        return [{"type": link.note, "url": link.url} for link in links]

    def get_presidents(self, obj):
        presidents = obj.query_members_by_role("president")
        serializer = CommonPersonSerializer(presidents, many=True, context=self.context)
        return serializer.data

    def get_deputies(self, obj):
        deputies = obj.query_members_by_role("deputy")
        serializer = CommonPersonSerializer(deputies, many=True, context=self.context)
        return serializer.data

    def get_number_of_members(self, obj):
        return obj.number_of_members_at(self.context["request_date"])

    number_of_members = serializers.SerializerMethodField()
    social_networks = serializers.SerializerMethodField()
    email = serializers.CharField()
    presidents = serializers.SerializerMethodField()
    deputies = serializers.SerializerMethodField()


class RootOrganizationBasicInfoSerializer(CommonSerializer):
    name = VersionableSerializerField(property_model_name="OrganizationName")
    email = VersionableSerializerField(property_model_name="OrganizationEmail")
    leader = serializers.SerializerMethodField()
    website = serializers.SerializerMethodField()
    budget = serializers.SerializerMethodField()

    def get_leader(self, obj):
        people = obj.query_members_by_role(role="leader")
        if people:
            return CommonPersonSerializer(people.first(), context=self.context).data
        else:
            raise Exception(f"There`s not a leader of this organization")

    def get_website(self, obj):
        website = Link.objects.filter(organization=obj, tags__name="website")
        return website.first().url if website else None

    def get_budget(self, obj):
        budget = Link.objects.filter(organization=obj, tags__name="budget")
        return budget.first().url if budget else None
