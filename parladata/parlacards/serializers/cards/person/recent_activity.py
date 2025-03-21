from django.db.models import F, Q, Value

from parlacards.pagination import create_paginator
from parlacards.serializers.common import PersonScoreCardSerializer
from parlacards.serializers.recent_activity import EventSerializer
from parladata.models.ballot import Ballot
from parladata.models.common import Mandate
from parladata.models.question import Question
from parladata.models.speech import Speech


class RecentActivityCardSerializer(PersonScoreCardSerializer):
    def get_results(self, person):
        # this is implemented in to_representation for pagination
        return None

    def to_representation(self, person):
        parent_data = super().to_representation(person)

        mandate = Mandate.get_active_mandate_at(self.context["request_date"])
        from_timestamp, to_timestamp = mandate.get_time_range_from_mandate(
            self.context["request_date"]
        )

        # get all events (questions, ballots, speeches) for person
        # Important: bacause we join all of them in a union, they all need to
        # have the same number and types of values {id, timestamp, type}
        questions = (
            Question.objects.filter(
                person_authors=person,
                mandate=mandate,
            )
            .filter(
                Q(timestamp__range=(from_timestamp, to_timestamp))
                | Q(timestamp__isnull=True),
            )
            .values("id", "timestamp")
            .annotate(type=Value("question"))
        )
        ballots = (
            Ballot.objects.filter(
                personvoter=person,
                vote__timestamp__range=(from_timestamp, to_timestamp),
            )
            .values("id", "vote__timestamp")
            .annotate(type=Value("ballot"))
        )
        speeches = (
            Speech.objects.filter_valid_speeches(self.context["request_date"])
            .filter(
                speaker=person,
                start_time__range=(from_timestamp, to_timestamp),
            )
            .values("id", "start_time")
            .annotate(type=Value("speech"))
        )

        # create a union of all events and sort them by timestamp (unions get
        # column names from first queryset, e.g. `timestamp` is from questions)
        ordered_event_ids = (
            questions.union(ballots)
            .union(speeches)
            .order_by(F("timestamp").desc(nulls_last=True), "id")
        )

        paged_event_ids, pagination_metadata = create_paginator(
            self.context.get("GET", {}), ordered_event_ids
        )

        # we need full db objects for serialization
        db_objects = {
            "question": Question.objects.filter(
                id__in=[o["id"] for o in paged_event_ids if o["type"] == "question"]
            ),
            "ballot": Ballot.objects.filter(
                id__in=[o["id"] for o in paged_event_ids if o["type"] == "ballot"]
            ),
            "speech": Speech.objects.filter(
                id__in=[o["id"] for o in paged_event_ids if o["type"] == "speech"]
            ),
        }

        # map from {id, timestamp, type} to full Question, Ballot, or Speech object
        paged_object_list = map(
            lambda id_object: next(
                db_object
                for db_object in db_objects[id_object["type"]]
                if db_object.id == id_object["id"]
            ),
            paged_event_ids,
        )

        event_serializer = EventSerializer(
            paged_object_list,
            many=True,
            context=self.context,
        )

        return {
            **parent_data,
            **pagination_metadata,
            "results": event_serializer.data,
        }
