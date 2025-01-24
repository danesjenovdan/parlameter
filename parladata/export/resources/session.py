from import_export.fields import Field

from export.resources.common import (
    ExportModelResource,
    get_cached_group_name,
    get_cached_person_name,
)
from parladata.models import Ballot, Speech, Vote


class VoteResource(ExportModelResource):
    def get_queryset(self, mandate_id=None, request_id=None):
        """
        Returns a queryset of all votes for given mandate id.
        Or returns all votes if there is no mandate id.
        """
        if mandate_id:
            votes = Vote.objects.filter(
                motion__session__mandate_id=mandate_id,
                motion__session_id=request_id,
            )
            return votes
        else:
            return Vote.objects.all()

    law_id = Field()

    class Meta:
        model = Vote
        fields = ("id", "name", "motion__text", "motion__summary", "result", "law_id")
        export_order = (
            "id",
            "name",
            "motion__text",
            "motion__summary",
            "result",
            "law_id",
        )

    def dehydrate_law_id(self, vote):
        return vote.motion.law.id if vote.motion.law else None


class SessionSpeechesResource(ExportModelResource):
    def get_queryset(self, mandate_id=None, request_id=None):
        """
        Returns a queryset of all speeches for given session id.
        """
        if request_id:
            return (
                Speech.objects.filter_valid_speeches()
                .filter(session_id=request_id)
                .order_by("order", "id")  # fallback ordering
            )
        return Speech.objects.none()

    speaker_name = Field()

    class Meta:
        model = Speech
        fields = (
            "id",
            "speaker__id",
            "speaker_name",
            "content",
            "start_time",
            "session__id",
            "session__name",
        )
        export_order = (
            "id",
            "speaker__id",
            "speaker_name",
            "content",
            "start_time",
            "session__id",
            "session__name",
        )

    def dehydrate_speaker_name(self, speech):
        return get_cached_person_name(speech.speaker.id)


class SingleVoteResource(ExportModelResource):
    """
    Returns a queryset of all ballots for given vote id.
    """

    def get_queryset(self, mandate_id=None, request_id=None):
        if request_id:
            if vote := Vote.objects.filter(id=request_id).first():
                return vote.ballots.all()
        return Ballot.objects.none()

    personvoter_name = Field()
    personvoter_group = Field()

    class Meta:
        model = Ballot
        fields = (
            "id",
            "personvoter__id",
            "personvoter_name",
            "personvoter_group",
            "option",
            "vote__motion__id",
            "vote__motion__title",
        )
        export_order = (
            "id",
            "personvoter__id",
            "personvoter_name",
            "personvoter_group",
            "option",
            "vote__motion__id",
            "vote__motion__title",
        )

    def dehydrate_personvoter_name(self, ballot):
        return get_cached_person_name(ballot.personvoter.id)

    def dehydrate_personvoter_group(self, ballot):
        person = ballot.personvoter
        group = person.parliamentary_group_on_date(timestamp=ballot.vote.timestamp)
        return get_cached_group_name(group.id) if group else None
