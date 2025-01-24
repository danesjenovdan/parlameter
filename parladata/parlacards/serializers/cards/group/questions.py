from django.core.cache import cache
from django.db.models import Q

from parlacards.pagination import calculate_cache_key_for_page, create_paginator
from parlacards.serializers.common import GroupScoreCardSerializer
from parlacards.serializers.question import QuestionSerializer
from parladata.models.common import Mandate
from parladata.models.question import Question


class GroupQuestionCardSerializer(GroupScoreCardSerializer):
    def get_results(self, obj):
        # this is implemented in to_representation for pagination
        return None

    # TODO this is very similar to GroupCardSerializer
    def to_representation(self, group):
        parent_data = super().to_representation(group)

        # set the relevant timestamp to filter the questions
        timestamp = self.context["request_date"]

        # get active madnate from timestamp and it's begining and ending/current timestamp
        mandate = Mandate.get_active_mandate_at(timestamp)
        from_timestamp, to_timestamp = mandate.get_time_range_from_mandate(timestamp)

        # get group member ids
        member_ids = group.query_members(timestamp).values_list("id", flat=True)

        # query all questions ever asked by the group's members
        all_member_questions = Question.objects.filter(
            Q(timestamp__range=(from_timestamp, to_timestamp))
            | Q(timestamp__isnull=True),
            person_authors__id__in=member_ids,
        ).prefetch_related("person_authors")

        if not all_member_questions.exists():
            # this "if" is an optimization
            # if there are no questions the whole function
            # takes 10 times longer to execute
            # this used to return []
            # which introduced a bug
            #
            # it needs to return a properly structured object
            # it's quite possible this sort of bug was produced
            # elsewhere
            #
            # also this whole function needs more comments
            # to explain why it's doing what it's doing
            paged_object_list, pagination_metadata = create_paginator(
                self.context.get("GET", {}), Question.objects.none()
            )
            return {**parent_data, **pagination_metadata, "results": []}

        # we need to filter out the questions for the timeframe when
        # the members were actually members of the group
        memberships = group.query_memberships_before(timestamp)

        # construct an empty Question queryset to union it in the future
        questions = Question.objects.none()

        # iterate through members and get their questions in the relevant time frame
        for member_id in member_ids:
            member_questions = all_member_questions.filter(person_authors__id=member_id)

            # if this person did not ask any questions there is no need to continue
            if not member_questions.exists():
                continue

            # get the person's membership start and end times
            member_memberships = memberships.filter(
                member_id=member_id, mandate=mandate
            ).values("start_time", "end_time")

            # iterate through the memberships and construct a Q object
            # with the appropriate start and end times
            q_objects = Q()
            for membership in member_memberships:
                q_params = {}
                if membership["start_time"]:
                    q_params["timestamp__gte"] = membership["start_time"]
                if membership["end_time"]:
                    q_params["timestamp__lte"] = membership["end_time"]
                q_objects.add(Q(**q_params), Q.OR)

            # add the filtered questions to the (once empty) questions queryset
            questions = questions.union(member_questions.filter(q_objects))

        # get all questions that were asked by the organization, not by individual members
        organization_questions = Question.objects.filter(
            Q(timestamp__range=(from_timestamp, to_timestamp))
            | Q(timestamp__isnull=True),
            organization_authors=group,
        )

        # union "organizational questions" with members' questions
        questions = questions.union(organization_questions)

        # annotate all the questions
        questions = (
            Question.objects.filter(id__in=questions.values("id"))
            .prefetch_related(
                "person_authors",
                "organization_authors",
                "recipient_people",
                "links",
            )
            .order_by("-timestamp")
        )

        # paginate the questions
        paged_object_list, pagination_metadata = create_paginator(
            self.context.get("GET", {}), questions
        )

        # calculate cache key for the page
        page_cache_key = f"GroupQuestionCardSerializer_{calculate_cache_key_for_page(paged_object_list, pagination_metadata)}"

        # if there's something in the cache return it, otherwise serialize and save to the cache
        if cached_members := cache.get(page_cache_key):
            page_data = cached_members
        else:
            question_serializer = QuestionSerializer(
                paged_object_list, many=True, context=self.context
            )
            page_data = question_serializer.data
            cache.set(page_cache_key, page_data)

        return {
            **parent_data,
            **pagination_metadata,
            "results": page_data,
        }
