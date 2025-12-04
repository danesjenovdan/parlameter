from django.db.models import Q
from rest_framework import serializers

from parlacards.serializers.common import (
    CommonCachableSerializer,
    CommonOrganizationSerializer,
)
from parladata.models.agenda_item import AgendaItem
from parladata.models.vote import Vote


class SessionJointPartSerializer(serializers.Serializer):
    name = serializers.CharField()
    organization = CommonOrganizationSerializer()


class SessionSerializer(CommonCachableSerializer):
    def calculate_cache_key(self, session):
        dates = list(session.organizations.all().values_list("updated_at", flat=True))
        dates.append(session.updated_at)

        last_speech = session.speeches.all().order_by("updated_at").last()
        if last_speech:
            dates.append(last_speech.updated_at)

        last_motion = session.motions.all().order_by("updated_at").last()
        if last_motion:
            dates.append(last_motion.updated_at)

        last_agenda_item = (
            AgendaItem.objects.filter(session=session).order_by("updated_at").last()
        )
        if last_agenda_item:
            dates.append(last_agenda_item.updated_at)

        timestamp = max(dates)

        return (
            f'SessionSerializer_{session.id}_{timestamp.strftime("%Y-%m-%dT%H:%M:%S")}'
        )

    def get_has_transcript(self, session):
        return session.speeches.exists()

    def get_has_agenda_items(self, session):
        # do any agenda items exist for this session?
        return AgendaItem.objects.filter(session=session).exists()

    def get_has_minutes(self, session):
        # do any agenda items that have actual text content exist?
        return (
            AgendaItem.objects.filter(session=session)
            .exclude(Q(text__isnull=True) | Q(text__exact=""))
            .exists()
        )

    def get_has_legislation(self, session):
        return session.legislation_considerations.filter(
            Q(timestamp__lte=self.context["request_date"]) | Q(timestamp__isnull=True)
        ).exists()

    def get_has_votes(self, session):
        return Vote.objects.filter(motion__session=session).exists()

    def get_joint_data(self, session):
        if session.is_joint_session:
            return SessionJointPartSerializer(
                session.session_organization_through.all(),
                context=self.context,
                many=True,
            ).data
        else:
            return None

    name = serializers.CharField()
    joint_data = serializers.SerializerMethodField()
    id = serializers.IntegerField()
    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()
    organizations = CommonOrganizationSerializer(many=True)
    classification = (
        serializers.CharField()
    )  # TODO regular, irregular, urgent, correspondent
    in_review = serializers.BooleanField()
    has_transcript = serializers.SerializerMethodField()
    has_agenda_items = serializers.SerializerMethodField()
    has_minutes = serializers.SerializerMethodField()
    has_legislation = serializers.SerializerMethodField()
    has_votes = serializers.SerializerMethodField()
