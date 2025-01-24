from rest_framework import serializers

from parlacards.models import SessionGroupAttendance
from parlacards.serializers.common import CommonOrganizationSerializer, CommonSerializer


class SessionGroupAttendanceSerializer(CommonSerializer):
    value = serializers.FloatField()
    group = CommonOrganizationSerializer()
