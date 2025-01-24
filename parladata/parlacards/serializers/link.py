from rest_framework import serializers

from parlacards.serializers.tag import TagSerializer
from parladata.models.link import Link


class LinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Link
        fields = ["id", "url", "name", "tags"]

    tags = TagSerializer(many=True)
