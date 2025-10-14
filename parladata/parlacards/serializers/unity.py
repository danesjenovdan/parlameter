from datetime import datetime

from django.core.cache import cache
from django.db.models import Avg
from rest_framework import serializers
from rest_framework.exceptions import NotFound

from parlacards.models import GroupUnity
from parlacards.serializers.common import CommonOrganizationSerializer
from parladata.exceptions import NoMembershipException
from parladata.models.organization import Organization


class GroupUnityScoreSerializerField(serializers.Field):
    def __init__(self, **kwargs):
        kwargs["source"] = "*"
        kwargs["read_only"] = True
        super().__init__(**kwargs)

    def calculate_cache_key(self, group_id, timestamp):
        # something like NumberOfSpokenWords_12_2021-11-13-21
        # group_id is the id of the person or organization this score belongs to
        return f'GroupUnity_{group_id}_{timestamp.strftime("%Y-%m-%dT%H")}'

    def to_representation(self, group):
        if "request_date" not in self.context.keys():
            raise Exception(f"You need to provide a date in the serializer context.")

        # check for cache
        cache_key = self.calculate_cache_key(group.id, self.context["request_date"])
        cached_content = cache.get(cache_key)
        if cached_content:
            return cached_content

        # find all relevant groups
        try:
            playing_field, mandate = group.get_last_playing_field_with_mandate(
                self.context["request_date"]
            )
        except NoMembershipException as e:
            raise NotFound(detail=str(e), code=404)

        relevant_groups = playing_field.query_organization_members(
            timestamp=mandate.ending or self.context["request_date"]
        ).filter(classification="pg")

        # calculate averages for all groups
        group_averages = {}
        for loop_group in relevant_groups:
            group_averages[loop_group.id] = {
                "group": loop_group,
                "average_unity": GroupUnity.objects.filter(
                    group=loop_group,
                    timestamp__gte=mandate.beginning,
                    timestamp__lte=mandate.ending or datetime.strptime("3000", "%Y"),
                ).aggregate(Avg("value"))["value__avg"],
            }

        try:
            score = group_averages[group.id]["average_unity"]
        except KeyError:
            raise NotFound(
                detail="No unity score was calculated for this parliamentary group.",
                code=404,
            )

        average_score = sum(
            [avg["average_unity"] for avg in group_averages.values() if avg["average_unity"]]
        ) / len(group_averages.keys())

        # get the maximum score and the id of the groups in one loop
        maximum_score = -1
        winner_ids = []
        for group_average_key, group_average_value in group_averages.items():
            if group_average_value["average_unity"] > maximum_score:
                maximum_score = group_average_value["average_unity"]
                winner_ids = [group_average_key]
            elif group_average_value["average_unity"] == maximum_score:
                winner_ids.append(group_average_key)

        maximum_competitors = Organization.objects.filter(id__in=winner_ids)[
            :8
        ]  # max 8 fit inside the bar in card
        winners_serializer = CommonOrganizationSerializer(
            maximum_competitors, many=True, context=self.context
        )

        output = {
            "score": score,
            "average": average_score,
            "maximum": {
                "score": maximum_score,
                "groups": winners_serializer.data,
            },
        }

        cache.set(cache_key, output)
        return output
