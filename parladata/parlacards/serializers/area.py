from rest_framework import serializers

from parlacards.serializers.common import CommonSerializer


class AreaSerializer(CommonSerializer):
    name = serializers.CharField()
    classification = serializers.CharField()
    slug = serializers.CharField()
