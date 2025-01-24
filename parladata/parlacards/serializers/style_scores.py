from rest_framework import serializers

from parlacards.models import GroupStyleScore, PersonStyleScore
from parlacards.serializers.common import CommonSerializer
from parladata.models.organization import Organization
from parladata.models.person import Person


class StyleScoresSerializer(CommonSerializer):
    def get_style_score(self, person_or_group, style):
        if isinstance(person_or_group, Person):
            score = PersonStyleScore.objects.filter(
                person=person_or_group,
                style=style,
                timestamp__lte=self.context["request_date"],
            ).first()
        elif isinstance(person_or_group, Organization):
            score = GroupStyleScore.objects.filter(
                group=person_or_group,
                style=style,
                timestamp__lte=self.context["request_date"],
            ).first()
        else:
            raise Exception(
                f"You should supply a person or an organization. Instead you supplied {person_or_group}."
            )

        if not score:
            return None

        return score.value

    def get_problematic(self, obj):
        # obj is person or group
        return self.get_style_score(obj, "problematic")

    def get_simple(self, obj):
        # obj is person or group
        return self.get_style_score(obj, "simple")

    def get_sophisticated(self, obj):
        # obj is person or group
        return self.get_style_score(obj, "sophisticated")

    problematic = serializers.SerializerMethodField()
    simple = serializers.SerializerMethodField()
    sophisticated = serializers.SerializerMethodField()
