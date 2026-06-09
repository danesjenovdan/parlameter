from datetime import datetime

from django.db.models import Q
from import_export.fields import Field

from export.resources.common import (
    CardExport,
    get_cached_group_name,
    get_cached_person_name,
)
from parlacards.models import (
    AgreementWithGroup,
    GroupMonthlyVoteAttendance,
    GroupNumberOfQuestions,
    GroupStyleScore,
    GroupTfidf,
    GroupUnity,
    GroupVoteAttendance,
    GroupVotingDistance,
)
from parladata.models import Link, Organization, PersonMembership
from parladata.models.common import Mandate


class GroupCardExport(CardExport):
    name = Field()

    def get_queryset(self, mandate_id=None, request_id=None):
        queryset = super().get_queryset(mandate_id=mandate_id)
        return queryset.filter(group_id=request_id).order_by("-timestamp")

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
        return get_cached_group_name(score.group_id)


class GroupUnityResource(GroupCardExport):
    class Meta:
        model = GroupUnity
        fields = (
            "group",
            "vote",
            "value",
            "timestamp",
        )
        export_order = (
            "group",
            "vote",
            "value",
            "timestamp",
        )


class GroupNumberOfQuestionsResource(GroupCardExport):
    class Meta:
        model = GroupNumberOfQuestions


class GroupMonthlyVoteAttendanceResource(GroupCardExport):
    class Meta:
        model = GroupMonthlyVoteAttendance


class GroupVoteAttendanceResource(GroupCardExport):
    class Meta:
        model = GroupVoteAttendance


class GroupVotesInCommonResource(GroupCardExport):
    target_person = Field()

    class Meta:
        model = GroupVotingDistance
        fields = (
            "name",
            "target_person",
            "value",
            "timestamp",
        )
        export_order = (
            "name",
            "target_person",
            "value",
            "timestamp",
        )

    def dehydrate_target_person(self, score):
        return get_cached_person_name(score.target_id)


class GroupTfidfResource(GroupCardExport):
    class Meta:
        model = GroupTfidf
        fields = (
            "name",
            "token",
            "value",
            "timestamp",
        )
        export_order = (
            "name",
            "token",
            "value",
            "timestamp",
        )


class GroupStyleScoresResource(GroupCardExport):
    style = Field()

    class Meta:
        model = GroupStyleScore
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


class GroupInfoResource(CardExport):
    name = Field()
    acronym = Field()
    email = Field()
    facebook = Field()
    twitter = Field()

    def get_queryset(self, mandate_id=None, request_id=None):
        return self._meta.model.objects.filter(id=request_id)

    class Meta:
        model = Organization
        fields = ("name", "acronym", "email", "facebook", "twitter")
        export_order = ("name", "acronym", "email", "facebook", "twitter")

    def dehydrate_style(self, group):
        return group.name

    def dehydrate_acronym(self, group):
        return group.acronym

    def dehydrate_email(self, group):
        return group.email

    def dehydrate_facebook(self, group):
        fb_link = Link.objects.filter(organization=group, tags__name="fb").first()
        return fb_link.url if fb_link else None

    def dehydrate_twitter(self, group):
        tw_link = Link.objects.filter(organization=group, tags__name="tw").first()
        return tw_link.url if tw_link else None


class GroupMembersResource(CardExport):
    name = Field()
    organization = Field()
    on_behalf_of = Field()
    start_time = Field()
    end_time = Field()
    mandate = Field()

    def get_queryset(self, mandate_id=None, request_id=None):
        queryset = self._meta.model.objects.filter(mandate_id=mandate_id)
        queryset = queryset.filter(
            Q(organization_id=request_id) | Q(on_behalf_of=request_id)
        ).order_by("-start_time")
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


class GroupAgreementWithGroupResource(CardExport):
    name = Field()

    def get_queryset(self, mandate_id=None, request_id=None):
        group = Organization.objects.filter(id=request_id).first()
        mandate = Mandate.objects.filter(id=mandate_id).first()
        people = group.query_members()
        from_timestamp, to_timestamp = mandate.get_time_range_from_mandate(
            datetime.now()
        )

        relevant_agreement_querysets = [
            AgreementWithGroup.objects.filter(
                timestamp__range=(from_timestamp, to_timestamp), person=person
            )
            for person in people
        ]
        relevant_agreement_ids = (
            AgreementWithGroup.objects.none()
            .union(*relevant_agreement_querysets)
            .values("id")
        )
        relevant_agreements = AgreementWithGroup.objects.filter(
            id__in=relevant_agreement_ids
        ).order_by("-timestamp")
        return relevant_agreements

    class Meta:
        model = AgreementWithGroup
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
