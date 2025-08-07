from datetime import datetime, timedelta

from django.db.models import Q
from import_export.fields import Field

from export.resources.common import ExportModelResource, get_cached_person_name
from parlacards.models import (
    DeviationFromGroup,
    GroupNumberOfQuestions,
    GroupUnity,
    GroupVocabularySize,
    GroupVoteAttendance,
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
    Law,
    Mandate,
    Organization,
    OrganizationMembership,
    Person,
    PersonMembership,
    PublicPersonQuestion,
    Question,
    Session,
    Vote,
)
from parladata.models.person import Person


class MPResource(ExportModelResource):
    name = Field()
    age = Field()
    education_level = Field()
    preferred_pronoun = Field()
    number_of_mandates = Field()

    speeches_per_session = Field()
    number_of_questions = Field()
    mismatch_of_pg = Field()
    presence_votes = Field()
    spoken_words = Field()
    vocabulary_size = Field()

    def get_queryset(self, mandate_id=None, request_id=None):
        """
        Returns a queryset of all parliament members for given mandate id.
        Or returns all persons if there is no mandate id.
        """
        if not mandate_id:
            mandate_id = Mandate.objects.last()
        try:
            mandate = Mandate.objects.get(id=mandate_id)
            from_timestamp, to_timestamp = mandate.get_time_range_from_mandate(
                datetime.now()
            )
            before_end = to_timestamp - timedelta(minutes=1)
            root_organization, playing_field = mandate.query_root_organizations(
                before_end
            )
            members = playing_field.query_members(before_end)
            self.people = playing_field.query_voters(before_end)
            self.playing_field = playing_field
            return members
        # if mandate does not exist return empty queryset
        except:
            self.people = None
            self.playing_field = None
            return Person.objects.none()

    class Meta:
        model = Person
        fields = (
            "id",
            "name",
            "date_of_birth",
            "age",
            "education_level",
            "preferred_pronoun",
            "number_of_mandates",
            "speeches_per_session",
            "number_of_questions",
            "mismatch_of_pg",
            "presence_votes",
            "spoken_words",
            "vocabulary_size",
        )
        export_order = (
            "id",
            "name",
            "date_of_birth",
            "age",
            "education_level",
            "preferred_pronoun",
            "number_of_mandates",
            "speeches_per_session",
            "number_of_questions",
            "mismatch_of_pg",
            "presence_votes",
            "spoken_words",
            "vocabulary_size",
        )

    def dehydrate_name(self, person):
        return person.name

    def dehydrate_age(self, person):
        if person.date_of_birth:
            return int((datetime.now().date() - person.date_of_birth).days / 365.2425)
        return None

    def get_score(self, ScoreModel, person):
        latest_scores = ScoreModel.objects.filter(
            person=person,
            playing_field=self.playing_field,
        ).order_by("-timestamp")
        if latest_scores.exists():
            latest_score = latest_scores.latest("created_at")
            return latest_score.value
        else:
            return None

    def dehydrate_education_level(self, person):
        return person.education_level

    def dehydrate_preferred_pronoun(self, person):
        return person.preferred_pronoun

    def dehydrate_number_of_mandates(self, person):
        return person.number_of_mandates

    def dehydrate_speeches_per_session(self, person):
        return self.get_score(PersonAvgSpeechesPerSession, person)

    def dehydrate_number_of_questions(self, person):
        return self.get_score(PersonNumberOfQuestions, person)

    def dehydrate_mismatch_of_pg(self, person):
        return self.get_score(DeviationFromGroup, person)

    def dehydrate_presence_votes(self, person):
        return self.get_score(PersonVoteAttendance, person)

    def dehydrate_spoken_words(self, person):
        return self.get_score(PersonNumberOfSpokenWords, person)

    def dehydrate_vocabulary_size(self, person):
        return self.get_score(PersonVocabularySize, person)


class GroupsResource(ExportModelResource):
    name = Field()
    acronym = Field()
    number_of_members_at = Field()
    intra_disunion = Field()
    vocabulary_size = Field()
    number_of_questions = Field()
    vote_attendance = Field()

    def get_queryset(self, mandate_id=None, request_id=None):
        """
        Returns a queryset of all parliament groups for given mandate id.
        Or returns all groups if there is no mandate id.
        """
        if mandate_id:
            try:
                mandate = Mandate.objects.get(id=mandate_id)
                from_timestamp, to_timestamp = mandate.get_time_range_from_mandate(
                    datetime.now()
                )
                before_end = to_timestamp - timedelta(minutes=1)
                root_organization, playing_field = mandate.query_root_organizations(
                    before_end
                )
                organizations = playing_field.query_parliamentary_groups(before_end)
                self.playing_field = playing_field
                return organizations
            # if mandate does not exist return empty queryset
            except:
                return Organization.objects.none()
        else:
            memberships = OrganizationMembership.objects.filter(
                organization__classification="root"
            ).values_list("member__id", flat=True)
            return Organization.objects.filter(id__in=memberships)

    class Meta:
        model = Organization
        fields = (
            "id",
            "name",
            "acronym",
            "number_of_members_at",
            "intra_disunion",
            "vocabulary_size",
            "number_of_questions",
            "vote_attendance",
        )
        export_order = ("id", "name", "acronym", "number_of_members_at")

    def get_group_score(self, ScoreModel, group):
        scores = ScoreModel.objects.filter(
            group_id=group.id,
            playing_field=self.playing_field,
        )
        if scores:
            latest_scores = scores.order_by("-timestamp").latest("created_at")
            return latest_scores.value
        return None

    def dehydrate_name(self, organization):
        return organization.name

    def dehydrate_acronym(self, organization):
        return organization.acronym

    def dehydrate_number_of_members_at(self, organization):
        return organization.number_of_members_at()

    def dehydrate_intra_disunion(self, organization):
        return self.get_group_score(GroupUnity, organization)

    def dehydrate_vocabulary_size(self, organization):
        return self.get_group_score(GroupVocabularySize, organization)

    def dehydrate_number_of_questions(self, organization):
        return self.get_group_score(GroupNumberOfQuestions, organization)

    def dehydrate_vote_attendance(self, organization):
        return self.get_group_score(GroupVoteAttendance, organization)


class MembershipResource(ExportModelResource):
    member = Field()
    start_time = Field()
    end_time = Field()
    organization = Field()
    on_behalf_of = Field()
    role = Field()

    def get_queryset(self, mandate_id=None, request_id=None):
        """
        Returns a queryset of all memberships for given mandate id.
        Or returns all memberships if there is no mandate id.
        """
        if mandate_id:
            votes = PersonMembership.objects.filter(mandate=mandate_id)
            return votes
        else:
            return PersonMembership.objects.all()

    class Meta:
        model = PersonMembership
        fields = (
            "id",
            "start_time",
            "end_time",
            "organization",
            "on_behalf_of",
            "member",
            "role",
        )
        export_order = (
            "id",
            "start_time",
            "end_time",
            "organization",
            "on_behalf_of",
            "member",
            "role",
        )

    def dehydrate_member(self, membership):
        return membership.member.name if membership.member else None

    def dehydrate_organization(self, membership):
        return membership.organization.name if membership.organization else None

    def dehydrate_on_behalf_of(self, membership):
        return membership.on_behalf_of.name if membership.on_behalf_of else None


class SessionResource(ExportModelResource):
    organizations = Field()

    def get_queryset(self, mandate_id=None, request_id=None):
        """
        Returns a queryset of all sessions for given mandate id.
        Or returns all sessions if there is no mandate id.
        """
        if mandate_id:
            sessions = Session.objects.filter(mandate=mandate_id)
            return sessions
        else:
            return Session.objects.all()

    class Meta:
        model = Session
        fields = (
            "id",
            "name",
            "organizations",
            "start_time",
            "classification",
            "in_review",
        )
        export_order = (
            "id",
            "name",
            "organizations",
            "start_time",
            "classification",
            "in_review",
        )

    def dehydrate_organizations(self, session):
        return " & ".join(
            list(session.organizations.values_list("latest_name", flat=True))
        )


class LegislationResource(ExportModelResource):
    classification = Field()
    procedure_phase = Field()
    text = Field()
    epa = Field()
    passed = Field()
    timestamp = Field()
    classification = Field()

    def get_queryset(self, mandate_id=None, request_id=None):
        """
        Returns a queryset of legislation for given mandate id.
        Or returns all legislation if there is no mandate id.
        """
        if mandate_id:
            legislation = Law.objects.filter(
                Q(legislationconsideration__session__mandate_id=mandate_id)
                | Q(mandate_id=mandate_id)
            )
            if request_id:
                legislation = legislation.filter(
                    legislationconsideration__session_id=request_id
                )
            return legislation
        else:
            return Law.objects.all()

    class Meta:
        model = Law
        fields = (
            "id",
            "text",
            "epa",
            "passed",
            "classification",
            "timestamp",
            "procedure_phase",
        )
        export_order = (
            "id",
            "text",
            "epa",
            "passed",
            "classification",
            "timestamp",
            "procedure_phase",
        )

    def dehydrate_classification(self, legislation):
        return legislation.classification.name if legislation.classification else ""

    def dehydrate_procedure_phase(self, legislation):
        procedure_phase = legislation.considerations.last()
        if procedure_phase:
            return procedure_phase.name
        else:
            return ""

    def dehydrate_text(self, legislation):
        return legislation.text

    def dehydrate_passed(self, legislation):
        return legislation.passed

    def dehydrate_epa(self, legislation):
        return legislation.epa

    def dehydrate_timestamp(self, legislation):
        return legislation.timestamp.isoformat() if legislation.timestamp else ""
