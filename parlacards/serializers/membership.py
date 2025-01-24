from rest_framework import serializers

from parlacards.serializers.common import CommonOrganizationSerializer, CommonSerializer


class MembershipSerializer(CommonSerializer):
    def get_organization(self, obj):
        return CommonOrganizationSerializer(obj.organization, context=self.context).data

    def get_on_behalf_of(self, obj):
        return CommonOrganizationSerializer(obj.on_behalf_of, context=self.context).data

    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()
    role = serializers.CharField()
    organization = serializers.SerializerMethodField()
    on_behalf_of = serializers.SerializerMethodField()
