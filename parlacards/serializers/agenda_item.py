from django.db.models import Q
from rest_framework import serializers

from parlacards.serializers.common import CommonCachableSerializer, CommonSerializer
from parlacards.serializers.link import LinkSerializer
from parlacards.serializers.session import SessionSerializer
from parlacards.serializers.tag import TagSerializer
from parlacards.serializers.vote import SpeechVoteSerializer
from parladata.models.agenda_item import AgendaItem
from parladata.models.link import Link
from parladata.models.vote import Vote


class CommonAgendaItemSerializer(CommonSerializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    order = serializers.IntegerField()
    text = serializers.CharField()


class AgendaItemSerializer(CommonAgendaItemSerializer):
    tags = TagSerializer(many=True)
    documents = serializers.SerializerMethodField()

    def get_documents(self, obj):
        link_ids = (
            Link.objects.filter(Q(agenda_item=obj) | Q(motion__in=obj.motions.all()))
            .distinct("url")
            .exclude(tags__name="vote-pdf")
            .values_list("id")
        )
        links = Link.objects.filter(id__in=link_ids).order_by("id")
        return LinkSerializer(links, many=True).data


class BaseMinutesAgendaItemSerializer(CommonAgendaItemSerializer):
    votes = serializers.SerializerMethodField()

    def get_votes(self, agenda_item):
        votes = Vote.objects.filter(motion__agenda_items=agenda_item)
        return SpeechVoteSerializer(votes, many=True).data


class MinutesAgendaItemSerializer(
    BaseMinutesAgendaItemSerializer, CommonCachableSerializer
):
    def calculate_cache_key(self, agenda_item):
        timestamp = agenda_item.updated_at
        last_vote = (
            Vote.objects.filter(motion__agenda_items=agenda_item)
            .order_by("updated_at")
            .last()
        )
        if last_vote:
            timestamp = max([timestamp, last_vote.updated_at])
        return f'MinutesAgendaItemSerializer_{agenda_item.id}_{timestamp.strftime("%Y-%m-%dT%H:%M:%S")}'


class MinutesAgendaItemWithSessionSerializer(
    BaseMinutesAgendaItemSerializer, CommonCachableSerializer
):
    session = serializers.SerializerMethodField()

    def get_session(self, agenda_item):
        serializer = SessionSerializer(agenda_item.session, context=self.context)
        return serializer.data

    def calculate_cache_key(self, agenda_item):
        timestamps = [agenda_item.updated_at, agenda_item.session.updated_at]

        last_vote = (
            Vote.objects.filter(motion__agenda_items=agenda_item)
            .order_by("updated_at")
            .last()
        )
        if last_vote:
            timestamps.append(last_vote.updated_at)

        timestamp = max(timestamps)
        return f'MinutesAgendaItemWithSessionSerializer_{agenda_item.id}_{timestamp.strftime("%Y-%m-%dT%H:%M:%S")}'


class MinutesAgendaItemWithSessionWithoutVotesSerializer(CommonAgendaItemSerializer):
    session = serializers.SerializerMethodField()

    def get_session(self, agenda_item):
        serializer = SessionSerializer(agenda_item.session, context=self.context)
        return serializer.data


class AgendaItemsSerializer(CommonCachableSerializer):
    agenda_items = serializers.SerializerMethodField()
    documents = serializers.SerializerMethodField()

    def calculate_cache_key(self, instance):
        # instance is the session
        times = [instance.updated_at]

        last_document = (
            Link.objects.filter(agenda_item__session=instance)
            .order_by("updated_at")
            .last()
        )

        if last_document:
            times.append(last_document.updated_at)

        agenda_items = instance.agenda_items.all()
        if agenda_items:
            times.append(agenda_items.latest("updated_at").updated_at)

        timestamp = max(times)
        return f'AgendaItemSerializer{instance.id}_{timestamp.strftime("%Y-%m-%dT%H:%M:%S")}'

    def get_agenda_items(self, obj):
        agenda_item_serializer = AgendaItemSerializer(
            AgendaItem.objects.filter(
                Q(datetime__lte=self.context["request_date"])
                | Q(datetime__isnull=True),
                session=obj,
            ).order_by("order"),
            context=self.context,
            many=True,
        )
        return agenda_item_serializer.data

    def get_documents(self, obj):
        links = obj.links.all().exclude(tags__name="vote-pdf").order_by("id")
        return LinkSerializer(links, many=True).data
