from rest_framework import serializers

from .common import (
    CommonOrganizationSerializer,
    CommonPersonSerializer,
    CommonSerializer,
)


class GroupFacetSerializer(CommonSerializer):
    group = CommonOrganizationSerializer()
    value = serializers.IntegerField()


class PersonFacetSerializer(CommonSerializer):
    person = CommonPersonSerializer()
    value = serializers.IntegerField()
