from rest_framework import serializers

from parlacards.serializers.common import CommonSerializer


class MediumSerializer(CommonSerializer):
    name = serializers.CharField()
    url = serializers.CharField()
    order = serializers.IntegerField()


class MediaReportSerializer(CommonSerializer):
    title = serializers.CharField()
    url = serializers.CharField()
    report_date = serializers.DateField()
    medium = MediumSerializer()
