from import_export.fields import Field

from export.resources.common import (
    CardExport,
    get_cached_group_name,
    get_cached_person_name,
)
from parlacards.models import (
    DeviationFromGroup,
    PersonAvgSpeechesPerSession,
    PersonMonthlyVoteAttendance,
    PersonNumberOfQuestions,
    PersonNumberOfSpokenWords,
    PersonStyleScore,
    PersonTfidf,
    PersonVocabularySize,
    PersonVoteAttendance,
    VotingDistance,
)
from parladata.models import (
    Ballot,
    Person,
    PersonMembership,
    PublicPersonQuestion,
    Question,
)


class PersonCardExport(CardExport):
    name = Field()

    def get_queryset(self, mandate_id=None, request_id=None):
        queryset = super().get_queryset(mandate_id=mandate_id)
        return queryset.filter(person_id=request_id).order_by("-timestamp")

    class Meta:
        fields = (
            "name",
            "value",
            "timestamp",
        )
        export_order = (
            "name",
            "value",
            "timestamp",
        )

    def dehydrate_name(self, score):
        return get_cached_person_name(score.person_id)


class PersonInfoCardResource(CardExport):
    name = Field()
    image = Field()
    education = Field()
    education_level = Field()
    previous_occupation = Field()
    number_of_mandates = Field()
    number_of_voters = Field()
    parliamentary_group = Field()

    def get_queryset(self, mandate_id=None, request_id=None):
        person = Person.objects.filter(id=request_id)
        if PersonMembership.objects.filter(
            member=person.first(), mandate_id=mandate_id
        ).exists():
            return person
        else:
            return Person.objects.none()

    class Meta:
        fields = (
            "name",
            "date_of_birth",
            "image",
            "education",
            "education_level",
            "previous_occupation",
            "number_of_mandates",
            "number_of_voters",
            "parliamentary_group",
        )
        export_order = (
            "name",
            "date_of_birth",
            "image",
            "education",
            "education_level",
            "previous_occupation",
            "number_of_mandates",
            "number_of_voters",
            "parliamentary_group",
        )
        model = Person

    def dehydrate_name(self, person):
        return get_cached_person_name(person.id)

    def dehydrate_image(self, person):
        return person.image.url

    def dehydrate_education(self, person):
        return person.education

    def dehydrate_education_level(self, person):
        return person.education_level

    def dehydrate_previous_occupation(self, person):
        return person.previous_occupation

    def dehydrate_number_of_mandates(self, person):
        return person.number_of_mandates

    def dehydrate_number_of_voters(self, person):
        return person.number_of_voters

    def dehydrate_parliamentary_group(self, person):
        return get_cached_group_name(person.parliamentary_group_on_date().id)


class PersonNumberOfSpokenWordsResource(PersonCardExport):
    class Meta:
        model = PersonNumberOfSpokenWords


class VocabularySizeResource(PersonCardExport):
    class Meta:
        model = PersonVocabularySize


class DeviationFromGroupResource(PersonCardExport):
    class Meta:
        model = DeviationFromGroup


class PersonMonthlyVoteAttendanceResource(PersonCardExport):
    class Meta:
        model = PersonMonthlyVoteAttendance


class PersonVoteAttendanceResource(PersonCardExport):
    class Meta:
        model = PersonVoteAttendance


class PersonStyleScoresResource(PersonCardExport):
    class Meta:
        model = PersonStyleScore
        fields = (
            "name",
            "style",
            "value",
            "timestamp",
        )
        export_order = (
            "name",
            "style",
            "value",
            "timestamp",
        )

    def dehydrate_style(self, score):
        return score.style


class PersonAvgSpeechesPerSessionResource(PersonCardExport):
    class Meta:
        model = PersonAvgSpeechesPerSession


class VotingDistanceResource(PersonCardExport):
    distance_with = Field()

    class Meta:
        model = VotingDistance
        fields = (
            "name",
            "distance_with",
            "value",
            "timestamp",
        )
        export_order = (
            "name",
            "distance_with",
            "value",
            "timestamp",
        )

    def dehydrate_distance_with(self, score):
        return get_cached_person_name(score.target_id)


class PersonNumberOfQuestionsResource(PersonCardExport):
    class Meta:
        model = PersonNumberOfQuestions


class PersonPublicQuestionsResource(CardExport):
    name = Field()
    created_at = Field()
    approved_at = Field()
    text = Field()
    answer_text = Field()
    answer_at = Field()

    def get_queryset(self, mandate_id=None, request_id=None):
        queryset = super().get_queryset(mandate_id=mandate_id)
        return queryset.filter(recipient_person_id=request_id).order_by("-created_at")

    class Meta:
        model = PublicPersonQuestion
        fields = (
            "name",
            "created_at",
            "approved_at",
            "text",
            "answer_text",
            "answer_at",
        )
        export_order = (
            "name",
            "created_at",
            "approved_at",
            "text",
            "answer_text",
            "answer_at",
        )

    def dehydrate_name(self, obj):
        return get_cached_person_name(obj.recipient_person_id)

    def dehydrate_answer_text(self, obj):
        answer = obj.answer.first()
        if answer:
            return answer.text
        return ""

    def dehydrate_answer_at(self, obj):
        answer = obj.answer.first()
        if answer:
            return answer.created_at.isoformat()
        return ""


class PersonTfidfResource(PersonCardExport):
    token = Field()

    class Meta:
        model = PersonTfidf
        fields = (
            "name",
            "value",
            "token",
            "timestamp",
        )
        export_order = (
            "name",
            "value",
            "token",
            "timestamp",
        )


class PersonMembershipResource(CardExport):
    name = Field()
    organization = Field()
    on_behalf_of = Field()
    start_time = Field()
    end_time = Field()
    mandate = Field()

    def get_queryset(self, mandate_id=None, request_id=None):
        queryset = self._meta.model.objects.filter(mandate_id=mandate_id)
        queryset = queryset.filter(member_id=request_id).order_by("-start_time")
        return queryset

    class Meta:
        model = PersonMembership
        fields = (
            "name",
            "role",
            "organization",
            "on_behalf_of",
            "start_time",
            "end_time",
            "mandate",
        )
        export_order = (
            "name",
            "role",
            "organization",
            "on_behalf_of",
            "start_time",
            "end_time",
            "mandate",
        )

    def dehydrate_name(self, membership):
        return get_cached_person_name(membership.member_id)

    def dehydrate_organization(self, membership):
        return membership.organization.name

    def dehydrate_on_behalf_of(self, membership):
        return membership.on_behalf_of.name if membership.on_behalf_of else None

    def dehydrate_start_time(self, membership):
        return membership.start_time.isoformat() if membership.start_time else None

    def dehydrate_end_time(self, membership):
        return membership.end_time.isoformat() if membership.end_time else None

    def dehydrate_mandate(self, membership):
        return membership.mandate.description if membership.mandate else None


class PersonBallotsResource(CardExport):
    name = Field()
    vote_text = Field()
    timestamp = Field()
    passed = Field()

    def get_queryset(self, mandate_id=None, request_id=None):
        queryset = self._meta.model.objects.filter(
            vote__motion__session__mandate_id=mandate_id
        )
        queryset = queryset.filter(personvoter_id=request_id).order_by(
            "-vote__timestamp"
        )
        return queryset

    class Meta:
        model = Ballot
        fields = ("name", "vote_text", "option", "timestamp", "passed")
        export_order = ("name", "vote_text", "option", "timestamp", "passed")

    def dehydrate_name(self, ballot):
        return get_cached_person_name(ballot.personvoter_id)

    def dehydrate_vote_text(self, ballot):
        return ballot.vote.name

    def dehydrate_timestamp(self, ballot):
        return ballot.vote.timestamp.isoformat() if ballot.vote.timestamp else None

    def dehydrate_passed(self, ballot):
        return ballot.vote.motion.result


class PersonQuestionsResource(CardExport):
    authors = Field()
    recipient_people = Field()
    timestamp = Field()

    def get_queryset(self, mandate_id=None, request_id=None):
        queryset = self._meta.model.objects.filter(mandate_id=mandate_id)
        queryset = queryset.filter(person_authors__id=request_id).order_by("-timestamp")
        print(queryset)
        return queryset

    class Meta:
        model = Question
        fields = (
            "authors",
            "title",
            "type_of_question",
            "recipient_people",
            "recipient_text",
            "timestamp",
        )
        export_order = (
            "authors",
            "title",
            "type_of_question",
            "recipient_people",
            "recipient_text",
            "timestamp",
        )

    def dehydrate_authors(self, question):
        return ", ".join(
            [
                get_cached_person_name(author.id)
                for author in question.person_authors.all()
            ]
        )

    def dehydrate_recipient_people(self, question):
        return ", ".join(
            [
                get_cached_person_name(recipient.id)
                for recipient in question.recipient_people.all()
            ]
        )

    def dehydrate_timestamp(self, question):
        return question.timestamp.isoformat() if question.timestamp else None
