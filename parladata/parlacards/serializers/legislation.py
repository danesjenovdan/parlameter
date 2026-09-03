from django.db.models import Q
from rest_framework import serializers
from rest_framework.exceptions import NotFound

from parlacards.serializers.common import CommonCachableSerializer, CommonSerializer
from parlacards.serializers.link import LinkSerializer
from parlacards.serializers.vote import BareVoteSerializer
from parladata.models.link import Link
from parladata.models.summary import Summary
from parladata.models.vote import Vote


def _serialize_legislation_documents(legislation, context=None):
    links = (
        Link.objects.filter(
            Q(motion__law=legislation)
            | Q(legislation_consideration__legislation=legislation)
            | Q(legislation=legislation)
        )
        .exclude(tags__name="vote-pdf")
        .select_related("legislation_consideration__procedure_phase")
        .distinct("url")
    )

    documents = []
    for link in links:
        doc = LinkSerializer(link, context=context).data
        phase = None
        if link.legislation_consideration:
            phase = link.legislation_consideration.procedure_phase
        doc["group"] = phase.name if phase and phase.name else "law"
        documents.append(doc)
    return documents


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
    last_consideration = serializers.SerializerMethodField()

    def calculate_cache_key(self, legislation):
        return f'LegislationSerializer_{legislation.id}_{legislation.updated_at.strftime("%Y-%m-%dT%H:%M:%S")}'

    def get_status(self, obj):
        return obj.status.name if obj.status else None

    def get_classification(self, obj):
        return obj.classification.name if obj.classification else None

    def get_last_consideration(self, obj):
        last_consideration = (
            obj.legislationconsideration_set.exclude(timestamp__isnull=True)
            .order_by("-timestamp")
            .first()
        )
        return last_consideration.timestamp if last_consideration else None


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
        return _serialize_legislation_documents(obj, context=self.context)


class LegislationBasicInfoDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    text = serializers.CharField()
    epa = serializers.CharField()
    status = serializers.CharField(source="status.name")


class LegislationInfoSerializer(CommonCachableSerializer):
    epa = serializers.CharField()
    proposed_by = serializers.CharField(source="proposer_text")
    classification = serializers.SerializerMethodField()
    procedure_type = serializers.SerializerMethodField()
    timestamp = serializers.DateTimeField()
    tags = serializers.SerializerMethodField()

    def calculate_cache_key(self, legislation):
        return f'LegislationInfoSerializer_{legislation.id}_{legislation.updated_at.strftime("%Y-%m-%dT%H:%M:%S")}'

    def get_classification(self, obj):
        return obj.classification.name if obj.classification else None

    def get_procedure_type(self, obj):
        return obj.procedure_type.name if obj.procedure_type else None

    def get_tags(self, obj):
        return [tag.name for tag in obj.tags.all()]


class LegislationProcedureSerializer(CommonCachableSerializer):
    procedure_type = serializers.CharField(source="procedure_type.name")
    considerations = serializers.SerializerMethodField()
    future_considerations = serializers.SerializerMethodField()

    def calculate_cache_key(self, legislation):
        return f'LegislationProcedureSerializer_{legislation.id}_{legislation.updated_at.strftime("%Y-%m-%dT%H:%M:%S")}'

    def get_considerations(self, obj):
        considerations = (
            obj.legislationconsideration_set.all()
            .prefetch_related("procedure_phase")
            .distinct("procedure_phase", "timestamp")
            .order_by("timestamp")
        )
        return [
            {
                "id": consideration.id,
                "name": consideration.procedure_phase.name,
                "timestamp": consideration.timestamp,
            }
            for consideration in considerations
        ]

    def get_future_considerations(self, obj):
        last_consideration = (
            obj.legislationconsideration_set.all()
            .prefetch_related("procedure_phase")
            .distinct("procedure_phase", "timestamp")
            .order_by("timestamp")
            .last()
            .procedure_phase.name
        )
        # Show only the phases that come after the last consideration
        future_phases = []
        last_phase_found = False
        for phase in (
            obj.procedure_type.default_phases.all()
            .order_by("order")
            .prefetch_related("procedure_phase")
        ):
            if last_phase_found:
                future_phases.append(
                    {
                        "id": phase.procedure_phase.id,
                        "name": phase.procedure_phase.name,
                    }
                )
            if phase.procedure_phase.name == last_consideration:
                last_phase_found = True
        return future_phases


class LegislationDocumentsSerializer(CommonCachableSerializer):
    documents = serializers.SerializerMethodField()

    def calculate_cache_key(self, legislation):
        return f'LegislationDocsSerializer_{legislation.id}_{legislation.updated_at.strftime("%Y-%m-%dT%H:%M:%S")}'

    def get_documents(self, obj):
        return _serialize_legislation_documents(obj, context=self.context)


class LegislationSummarySerializer(CommonCachableSerializer):
    summary = serializers.SerializerMethodField()

    def calculate_cache_key(self, legislation):
        return f'LegislationSummarySerializer_{legislation.id}_{legislation.updated_at.strftime("%Y-%m-%dT%H:%M:%S")}'

    def get_summary(self, obj):
        links = Link.objects.filter(
            Q(legislation=obj) | Q(legislation_consideration__legislation=obj),
            Q(tags__name__icontains="proposal") | Q(tags__name__icontains="enacted"),
        )

        if links.exists():
            summary = Summary.objects.filter(link__in=links, is_approved=True)
            if summary:
                summary = summary.latest("created_at")
                return {
                    "text": summary.text,
                    "link": (
                        LinkSerializer(summary.link, context=self.context).data
                        if summary.link
                        else None
                    ),
                    "ai_model": summary.ai_model,
                    "ai_model_version": summary.ai_model_version,
                }
            else:
                return {
                    "text": None,
                    "link": LinkSerializer(
                        links.latest("created_at"), context=self.context
                    ).data,
                    "ai_model": None,
                    "ai_model_version": None,
                }
        raise NotFound("No approved summary found for this legislation.")
