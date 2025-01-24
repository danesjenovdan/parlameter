from rest_framework import serializers

from parlacards.serializers.common import CommonPersonSerializer


class VotingDistanceSerializer(serializers.Serializer):
    person = CommonPersonSerializer(source="target")
    value = serializers.FloatField()


class GroupVotingDistanceSerializer(serializers.Serializer):
    person = CommonPersonSerializer(source="target")
    value = serializers.FloatField()
