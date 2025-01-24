from datetime import datetime

from django.shortcuts import get_object_or_404
from rest_framework import serializers

from parlanotifications.models import Keyword, NotificationUser


class KeywordSerializer(serializers.ModelSerializer):
    accepted = serializers.SerializerMethodField()
    email = serializers.EmailField(write_only=True, required=False)
    uuid = serializers.UUIDField(write_only=True, required=False)

    class Meta:
        model = Keyword
        fields = [
            "id",
            "keyword",
            "user",
            "matching_method",
            "accepted",
            "email",
            "notification_frequency",
            "uuid",
        ]
        read_only_fields = ["user"]

    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        if uuid := data.pop("uuid", None):
            print(uuid)
            user = get_object_or_404(NotificationUser, uuid=uuid)
            data.update(accepted_at=datetime.now())
        elif email := data.pop("email", None):
            print(email)
            user, created = NotificationUser.objects.get_or_create(email=email)
        else:
            raise serializers.ValidationError("uuid or email must be provided")

        data.update({"user": user})
        return data

    def get_accepted(self, obj):
        return obj.accepted_at is not None
