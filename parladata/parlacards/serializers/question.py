from rest_framework import serializers

from parlacards.serializers.common import (
    CommonOrganizationSerializer,
    CommonPersonSerializer,
    CommonSerializer,
)
from parladata.models import Answer


class AnswerSerializer(CommonSerializer):
    person_authors = serializers.SerializerMethodField()
    organization_authors = serializers.SerializerMethodField()
    text = serializers.CharField()
    timestamp = serializers.DateTimeField()

    def get_person_authors(self, obj):
        return CommonPersonSerializer(
            obj.person_authors.all(), context=self.context, many=True
        ).data

    def get_organization_authors(self, obj):
        return CommonOrganizationSerializer(
            obj.organization_authors.all(), context=self.context, many=True
        ).data


class QuestionSerializer(CommonSerializer):
    def get_recipient_people(self, obj):
        return CommonPersonSerializer(
            obj.recipient_people.all(), context=self.context, many=True
        ).data

    def get_authors(self, obj):
        person_authors = CommonPersonSerializer(
            obj.person_authors.all(), context=self.context, many=True
        ).data
        organization_authors = CommonOrganizationSerializer(
            obj.organization_authors.all(), context=self.context, many=True
        ).data
        return person_authors + organization_authors

    def get_url(self, obj):
        link = obj.links.first()
        if link:
            return link.url
        else:
            return None

    def get_type(self, obj):
        return obj.type_of_question

    def get_answer(self, obj):
        answer = obj.answers.first()
        return AnswerSerializer(answer, context=self.context).data if answer else None

    # TODO check which fields we need
    timestamp = serializers.DateTimeField()
    answer_timestamp = serializers.DateTimeField()
    title = serializers.CharField()
    authors = serializers.SerializerMethodField()
    recipient_people = serializers.SerializerMethodField()
    recipient_text = serializers.CharField()
    url = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    answer = serializers.SerializerMethodField()
