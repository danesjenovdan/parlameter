from django.db.models import Q
from rest_framework import serializers

from parlacards.models import SessionGroupAttendance
from parlacards.pagination import create_paginator
from parlacards.serializers.cards.session.tfidf import SessionTfidfCardSerializer
from parlacards.serializers.common import CardSerializer, MandateSerializer
from parlacards.serializers.group_attendance import SessionGroupAttendanceSerializer
from parlacards.serializers.session import SessionSerializer
from parlacards.serializers.vote import SessionVoteSerializer
from parladata.models import Vote


class MiscLastSessionCardSerializer(CardSerializer):
    def get_last_session(self, organization):
        return (
            organization.sessions.filter(
                Q(motions__isnull=False) | Q(sessiontfidf_related__isnull=False)
            )
            .distinct("id", "start_time")
            .latest("start_time")
        )

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

    def get_results(self, organization):
        last_session = self.get_last_session(organization)

        # tfidf
        tfidf_serializer = SessionTfidfCardSerializer(
            last_session, context=self.context
        )
        tfidf_results = tfidf_serializer.get_results(last_session)

        # attendance
        attendances = SessionGroupAttendance.objects.filter(
            session=last_session,
            timestamp__lte=self.context["request_date"],
        )
        attendance_serializer = SessionGroupAttendanceSerializer(
            attendances, many=True, context=self.context
        )

        return {
            "tfidf": tfidf_results,
            "attendance": attendance_serializer.data,
            "votes": None,  # this is implemented in to_representation for pagination
        }

    def to_representation(self, instance):
        parent_data = super().to_representation(instance)

        # instance is the parent organization
        last_session = self.get_last_session(instance)

        votes = Vote.objects.filter(motion__session=last_session).order_by(
            "timestamp", "id"  # fallback ordering
        )

        paged_object_list, pagination_metadata = create_paginator(
            self.context.get("GET", {}), votes, prefix="votes:"
        )

        # serialize votes
        vote_serializer = SessionVoteSerializer(
            paged_object_list, many=True, context=self.context
        )

        return {
            **parent_data,
            **pagination_metadata,
            "results": {
                **parent_data["results"],
                "votes": vote_serializer.data,
            },
        }

    def get_session(self, organization):
        session = self.get_last_session(organization)
        serializer = SessionSerializer(session, context=self.context)
        return serializer.data

    session = serializers.SerializerMethodField()
