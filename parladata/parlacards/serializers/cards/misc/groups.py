from importlib import import_module

from django.db.models import Q
from rest_framework import serializers

from parlacards.models import (
    GroupUnity,
    GroupNumberOfQuestions,
    GroupVocabularySize,
    GroupVoteAttendance,
)
from parlacards.serializers.common import (
    CardSerializer,
    CommonOrganizationSerializer,
    MandateSerializer,
)
from parladata.models.memberships import PersonMembership


class GroupAnalysesSerializer(CommonOrganizationSerializer):
    def calculate_cache_key(self, group):
        all_analyses = (
            GroupUnity,
            GroupVocabularySize,
            GroupNumberOfQuestions,
            GroupVoteAttendance,
        )

        analysis_timestamps = []
        for analysis in all_analyses:
            if (
                analysis_object := analysis.objects.filter(group=group)
                .order_by("-timestamp")
                .first()
            ):
                analysis_timestamps.append(analysis_object.timestamp)

        last_membership = PersonMembership.objects.filter(
            Q(organization=group) | Q(on_behalf_of=group)
        ).latest("updated_at")

        timestamp = max(
            [group.updated_at, last_membership.updated_at, *analysis_timestamps]
        )

        playing_field = self.context["playing_field"]

        return f"GroupAnalysesSerializer_{group.id}_{playing_field.id}_{timestamp.isoformat()}"

    def get_group_value(self, group, property_model_name):
        scores_module = import_module("parlacards.models")
        ScoreModel = getattr(scores_module, property_model_name)

        score_object = (
            ScoreModel.objects.filter(
                group_id=group.id, timestamp__lte=self.context["request_date"]
            )
            .order_by("-timestamp")
            .first()
        )

        if score_object:
            return score_object.value
        return None

    def get_results(self, obj):
        return {
            "seat_count": obj.number_of_members_at(self.context["request_date"]),
            "intra_disunion": self.get_group_value(obj, "GroupUnity"),
            "number_of_amendments": None,  # TODO
            "vocabulary_size": self.get_group_value(obj, "GroupVocabularySize"),
            "number_of_questions": self.get_group_value(obj, "GroupNumberOfQuestions"),
            "vote_attendance": self.get_group_value(obj, "GroupVoteAttendance"),
        }

    results = serializers.SerializerMethodField()


class MiscGroupsCardSerializer(CardSerializer):
    def get_results(self, parent_organization):
        new_context = dict.copy(self.context)
        new_context["playing_field"] = parent_organization

        serializer = GroupAnalysesSerializer(
            parent_organization.query_parliamentary_groups(
                self.context["request_date"]
            ),
            many=True,
            context=new_context,
        )
        return serializer.data

    def get_mandate(self, playing_field):
        organization_membership = playing_field.organization_memberships.filter(
            organization__classification=None
        ).first()
        if organization_membership:
            mandate = organization_membership.mandate
        else:
            mandate = None
        serializer = MandateSerializer(mandate, context=self.context)
        return serializer.data
