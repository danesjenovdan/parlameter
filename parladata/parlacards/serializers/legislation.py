from django.db.models import Q
from rest_framework import serializers

from parlacards.serializers.common import CommonCachableSerializer, CommonSerializer
from parlacards.serializers.link import LinkSerializer
from parlacards.serializers.vote import BareVoteSerializer
from parladata.models.link import Link
from parladata.models.vote import Vote


class LegislationSerializer(CommonCachableSerializer):
    id = serializers.IntegerField()
    uid = serializers.CharField()
    text = serializers.CharField()
    epa = serializers.CharField()
    status = serializers.SerializerMethodField()
    passed = serializers.BooleanField()
    classification = serializers.SerializerMethodField()
    has_votes = serializers.BooleanField()
    has_abstract = serializers.BooleanField()
    timestamp = serializers.DateTimeField()

    def calculate_cache_key(self, legislation):
        return f'LegislationSerializer_{legislation.id}_{legislation.updated_at.strftime("%Y-%m-%dT%H:%M:%S")}'

    def get_status(self, obj):
        return obj.status.name if obj.status else None

    def get_classification(self, obj):
        return obj.classification.name if obj.classification else None


class LegislationDetailSerializer(LegislationSerializer):
    votes = serializers.SerializerMethodField()
    abstract = serializers.CharField()
    documents = serializers.SerializerMethodField()

    def calculate_cache_key(self, legislation):
        return f'LegislationDetailSerializer_{legislation.id}_{legislation.updated_at.strftime("%Y-%m-%dT%H:%M:%S")}'

    def get_votes(self, obj):
        votes = Vote.objects.filter(motion__law=obj)
        return BareVoteSerializer(votes, many=True, context=self.context).data

    def get_documents(self, obj):
        links = (
            Link.objects.filter(
                Q(motion__law=obj) | Q(legislation_consideration__legislation=obj)
            )
            .exclude(tags__name="vote-pdf")
            .distinct("url")
        )
        return LinkSerializer(links, many=True, context=self.context).data
