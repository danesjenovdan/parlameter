from rest_framework import serializers

from parlacards.serializers.common import CommonSerializer


class TfidfSerializer(CommonSerializer):
    token = serializers.CharField()
    value = serializers.FloatField()
