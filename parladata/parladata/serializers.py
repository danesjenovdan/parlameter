import json

from rest_framework import serializers
from taggit.models import Tag
from taggit.serializers import TaggitSerializer, TagListSerializerField

from parladata.models import *


class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = [
            "id",
            "created_at",
            "updated_at",
            "name",
            "parser_names",
            "date_of_birth",
            "image",
            "districts",
        ]


class SessionSerializer(serializers.ModelSerializer):
    organizations = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Organization.objects.all(), required=False
    )

    class Meta:
        model = Session
        fields = "__all__"

    def create(self, validated_data):
        organizations = validated_data.pop("organizations", [])
        session = Session.objects.create(**validated_data)

        # Create SessionOrganizationThrough entries with name=None
        for org in organizations:
            SessionOrganizationThrough.objects.create(
                session=session, organization=org, name=None
            )

        return session

    def update(self, instance, validated_data):
        organizations = validated_data.pop("organizations", None)

        # Update session fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update organizations if provided
        if organizations is not None:
            # Remove existing relationships
            SessionOrganizationThrough.objects.filter(session=instance).delete()

            # Create new relationships with name=None
            for org in organizations:
                SessionOrganizationThrough.objects.create(
                    session=instance, organization=org, name=None
                )

        return instance


# class OrganizationNameSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = OrganizationName
#         fields = '__all__'


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = [
            "id",
            "created_at",
            "updated_at",
            "name",
            "acronym",
            "gov_id",
            "classification",
            "parser_names",
            "dissolution_date",
            "founding_date",
            "description",
            "parent",
            "has_voters",
            "name",
            "acronym",
        ]

    def get_name(self, obj):
        return obj.name


class SpeechSerializer(TaggitSerializer, serializers.ModelSerializer):
    agenda_item_order = serializers.SerializerMethodField()
    tags = TagListSerializerField(required=False)

    class Meta:
        model = Speech
        fields = [
            "id",
            "created_at",
            "updated_at",
            "valid_from",
            "valid_to",
            "content",
            "order",
            "start_time",
            "end_time",
            "speaker",
            "session",
            "agenda_items",
            "agenda_item_order",
            "tags",
        ]

    def get_agenda_item_order(self, obj):
        if obj.agenda_items.first():
            return obj.agenda_items.first().order
        return 0


class AgendaItemSerializer(TaggitSerializer, serializers.ModelSerializer):
    tags = TagListSerializerField(required=False)

    class Meta:
        model = AgendaItem
        fields = "__all__"


class VoteSerializer(TaggitSerializer, serializers.ModelSerializer):
    tags = TagListSerializerField(required=False)
    results = serializers.SerializerMethodField()
    has_ballots = serializers.SerializerMethodField()
    has_anonymous_ballots = serializers.SerializerMethodField()

    class Meta:
        model = Vote
        fields = "__all__"

    def get_results(self, obj):
        return obj.get_option_counts()

    def get_has_ballots(self, obj):
        return bool(obj.ballots.count())

    def get_has_anonymous_ballots(self, obj):
        return obj.ballots.filter(personvoter=None).exists()


class BallotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ballot
        fields = "__all__"


class LinkSerializer(TaggitSerializer, serializers.ModelSerializer):
    tags = TagListSerializerField(required=False)

    class Meta:
        model = Link
        fields = "__all__"


class DocumentSerializer(TaggitSerializer, serializers.ModelSerializer):
    tags = TagListSerializerField(required=False)

    class Meta:
        model = Document
        fields = "__all__"


class MotionSerializer(serializers.ModelSerializer):
    vote = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    links = LinkSerializer(many=True, read_only=True)
    tags = TagListSerializerField(required=False)

    class Meta:
        model = Motion
        fields = "__all__"


class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = "__all__"


class PersonMembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonMembership
        fields = "__all__"


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = "__all__"


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = "__all__"


class EpaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Motion
        fields = ("epa",)

    def to_representation(self, data):
        res = super(EpaSerializer, self).to_representation(data)
        return res["epa"]


class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"


class OrganizationMembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationMembership
        fields = ("id", "member", "organization", "start_time", "end_time")


class MandateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mandate
        fields = "__all__"


class ProcedureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Procedure
        fields = "__all__"


class ProcedurePhaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcedurePhase
        fields = "__all__"


class LegislationConsiderationSerializer(serializers.ModelSerializer):
    class Meta:
        model = LegislationConsideration
        fields = "__all__"


class LegislationStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = LegislationStatus
        fields = ["id", "name"]


class LegislationClassificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = LegislationClassification
        fields = ["id", "name"]


class LawSerializer(serializers.ModelSerializer):
    class Meta:
        model = Law
        fields = "__all__"


class MediumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medium
        fields = "__all__"


class MediaReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaReport
        fields = "__all__"


class PublicPersonAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = PublicPersonAnswer
        fields = "__all__"


class PublicPersonQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PublicPersonQuestion
        fields = "__all__"
        extra_kwargs = {"author_email": {"write_only": True}}
