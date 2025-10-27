from django.db.models import Q

from parlacards.pagination import create_paginator
from parlacards.serializers.common import PersonScoreCardSerializer
from parlacards.serializers.question import QuestionSerializer
from parladata.models.common import Mandate
from parladata.models.question import Question


class PersonQuestionCardSerializer(PersonScoreCardSerializer):
    def get_results(self, person):
        # this is implemented in to_representation for pagination
        return None

    def to_representation(self, person):
        parent_data = super().to_representation(person)

        mandate = Mandate.get_active_mandate_at(self.context["request_date"])
        from_timestamp, to_timestamp = mandate.get_time_range_from_mandate(
            self.context["request_date"]
        )

        # TODO make timestamp required field for question
        questions = Question.objects.filter(
            Q(timestamp__range=(from_timestamp, to_timestamp))
            | Q(timestamp__isnull=True),
            person_authors=person,
            mandate=mandate,
        ).order_by("-timestamp")

        paged_object_list, pagination_metadata = create_paginator(
            self.context.get("GET", {}), questions
        )

        questions_serializer = QuestionSerializer(
            paged_object_list,
            many=True,
            context=self.context,
        )

        return {
            **parent_data,
            **pagination_metadata,
            "results": questions_serializer.data,
        }
