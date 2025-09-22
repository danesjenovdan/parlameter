from datetime import datetime

from colorfield.fields import ColorField
from django.db import models
from django.db.models import OuterRef, Q, Subquery
from django.utils.translation import gettext_lazy as _

from parladata.behaviors.models import (
    Parsable,
    Sluggable,
    Taggable,
    Timestampable,
    VersionableFieldsOwner,
)
from parladata.exceptions import NoMembershipException
from parladata.models.ballot import Ballot
from parladata.models.link import Link
from parladata.models.memberships import OrganizationMembership, PersonMembership
from parladata.models.person import Person
from parladata.models.versionable_properties import OrganizationName

CLASSIFICATIONS = [
    ("root", _("root")),
    ("pg", _("pg")),
    ("commission", _("commission")),
    ("committee", _("committee")),
    ("council", _("council")),
    ("delegation", _("delegation")),
    ("friendship_group", _("friendship_group")),
    ("investigative_commission", _("investigative_commission")),
    ("other", _("other")),
    ("coalition", _("coalition")),
    ("house", _("house")),
]


class ActiveAtQuerySet(models.QuerySet):
    def is_active_at(self, timestamp):
        return bool(
            self.filter(
                Q(founding_date__lte=timestamp) | Q(founding_date__isnull=True),
                Q(dissolution_date__gte=timestamp) | Q(dissolution_date__isnull=True),
            )
        )


class ExtendedManager(models.Manager):
    """
    It's manager that adds values to queryset objects
    """

    def get_queryset(self):
        """
        Subquery create nested select query. In this case query currently valid name of organization
        Query for name is sliced to one obect because you can subquery just a queryset and not a single object.
        Annotation adds inquired name to the organization objects.
        """
        latest_name = Subquery(
            OrganizationName.objects.filter(
                owner_id=OuterRef("id"),
            )
            .valid_at(datetime.now())
            .order_by("-valid_from")
            .values("value")[:1]
        )
        return (
            super()
            .get_queryset()
            .annotate(
                latest_name=latest_name,
            )
        )


class Organization(
    Timestampable, Taggable, Parsable, Sluggable, VersionableFieldsOwner
):
    """A group with a common purpose or reason
    for existence that goes beyond the set of people belonging to it.
    """

    gov_id = models.TextField(
        verbose_name=_("Gov website ID"),
        help_text=_("Gov website ID"),
        blank=True,
        null=True,
    )
    classification = models.TextField(
        verbose_name=_("classification"),
        help_text=_("Select an organization category, e.g. committee"),
        blank=True,
        null=True,
        choices=CLASSIFICATIONS,
    )
    # reference to "http://popoloproject.com/schemas/organization.json#"
    parent = models.ForeignKey(
        "Organization",
        verbose_name=_("Organization"),
        help_text=_(
            "Select the higher tier organization that contains this organization"
        ),
        blank=True,
        null=True,
        related_name="children",
        on_delete=models.CASCADE,
    )
    founding_date = models.DateTimeField(
        verbose_name=_("founding_date"),
        help_text=_("Select the date of founding"),
        blank=True,
        null=True,
    )
    dissolution_date = models.DateTimeField(
        verbose_name=_("dissolution_date"),
        help_text=_("Select the date of dissolution"),
        blank=True,
        null=True,
    )
    description = models.TextField(
        verbose_name=_("description"),
        help_text="Insert the description of the organization",
        blank=True,
        null=True,
    )
    color = ColorField(
        default="#09a2cc",
    )

    objects = ExtendedManager.from_queryset(ActiveAtQuerySet)()

    class Meta:
        verbose_name = _("organization")
        verbose_name_plural = _("organizations")

    @property
    def name(self):
        # just objects in queryset has latest_name attribute
        if hasattr(self, "latest_name"):
            return self.latest_name
        else:
            return self.versionable_property_value_on_date(
                owner=self,
                property_model_name="OrganizationName",
                datetime=datetime.now(),
            )

    @property
    def acronym(self):
        return self.versionable_property_value_on_date(
            owner=self,
            property_model_name="OrganizationAcronym",
            datetime=datetime.now(),
        )

    @property
    def email(self):
        return self.versionable_property_value_on_date(
            owner=self, property_model_name="OrganizationEmail", datetime=datetime.now()
        )

    # TODO make all membership queries depend on a date
    def number_of_members_at(self, timestamp=None):
        if not timestamp:
            timestamp = datetime.now()

        return (
            PersonMembership.valid_at(timestamp)
            .filter(organization=self, role__in=["member", "president", "deputy"])
            .distinct("member")
            .count()
        )

    def number_of_organization_members_at(self, timestamp=None):
        if not timestamp:
            timestamp = datetime.now()

        return (
            OrganizationMembership.valid_at(timestamp)
            .filter(organization=self)
            .distinct("member")
            .count()
        )

    def number_of_voters_at(self, timestamp=None):
        if not timestamp:
            timestamp = datetime.now()

        return (
            PersonMembership.valid_at(timestamp)
            .filter(organization=self, role="voter")
            .distinct("member")
            .count()
        )

    def number_of_organization_voters_at(self, timestamp=None):
        if not timestamp:
            timestamp = datetime.now()

        return (
            OrganizationMembership.valid_at(timestamp)
            .filter(organization=self, role="voter")
            .distinct("member")
            .count()
        )

    @property
    def has_voters(self):
        return bool(self.memberships.filter(role="voter"))

    # TODO maybe we need to run distinct here
    def query_members(self, timestamp=None):
        if not timestamp:
            timestamp = datetime.now()

        member_ids = (
            PersonMembership.valid_at(timestamp)
            .filter(organization=self)
            .values_list("member", flat=True)
        )
        return Person.objects.filter(id__in=member_ids)

    # we need this to get all the timestamps
    # of all the memberships before a given date
    #
    # why? to query speeches only for the time
    # when the speaker was a voter member of the organization
    def query_memberships_before(self, timestamp=None):
        if not timestamp:
            timestamp = datetime.now()

        return PersonMembership.valid_before(timestamp).filter(
            on_behalf_of=self, role="voter"
        )

    def query_organization_members(self, timestamp=None):
        if not timestamp:
            timestamp = datetime.now()

        member_ids = (
            OrganizationMembership.valid_at(timestamp)
            .filter(organization=self)
            .values("member")
        )

        return Organization.objects.filter(id__in=member_ids)

    def query_parliamentary_groups(self, timestamp=None):
        if not timestamp:
            timestamp = datetime.now()

        # sometimes we have groups without members
        # this crashes some serializers (like vote/single
        # because it can't calculate the max_option for all groups)
        # so if a group has no members it should be filtered out

        ids_of_groups_with_voters = (
            PersonMembership.objects.filter(
                models.Q(start_time__lte=timestamp) | models.Q(start_time__isnull=True),
                models.Q(end_time__gte=timestamp) | models.Q(end_time__isnull=True),
                organization__in=Organization.objects.filter(
                    classification="pg"
                ),  # TODO rename to parliamentary_group
            )
            .values_list("organization__id", flat=True)
            .distinct("organization__id")
        )

        return self.query_organization_members(timestamp).filter(
            id__in=ids_of_groups_with_voters
        )

    def query_voter_groups(self, timestamp=None):
        if not timestamp:
            timestamp = datetime.now()

        # sometimes we need a list of all parliamentary groups that have voters
        # in a working body, f.e. when calculating unity

        voters = self.query_voters(timestamp)
        groups = [v.parliamentary_group_on_date(timestamp) for v in voters]
        group_ids = [g.id for g in groups if g]

        return Organization.objects.filter(id__in=group_ids)

    def query_voters(self, timestamp=None):
        if not timestamp:
            timestamp = datetime.now()

        return self.query_members_by_role("voter", timestamp)

    def query_members_by_role(self, role, timestamp=None):
        if not timestamp:
            timestamp = datetime.now()

        member_ids = (
            PersonMembership.valid_at(timestamp)
            .filter(organization=self, role=role)
            .values_list("member", flat=True)
        )

        return Person.objects.filter(id__in=member_ids)

    def query_organizations_by_role(self, role, timestamp=None):
        if not timestamp:
            timestamp = datetime.now()

        member_ids = (
            OrganizationMembership.valid_at(timestamp)
            .filter(organization=self, role=role)
            .values_list("member", flat=True)
        )

        return Organization.objects.filter(id__in=member_ids)

    def __str__(self):
        return f"{self.name} {self.id} {self.acronym}"

    def query_ballots_on_vote(self, vote):
        voter_ids = self.query_voters(vote.timestamp)
        return Ballot.objects.filter(vote=vote, personvoter__in=voter_ids)

    def query_root_organization_on_date(self, timestamp):
        return (
            OrganizationMembership.valid_at(timestamp)
            .filter(
                organization__classification="house",
                member=self,
            )
            .first()
        )

    def get_last_playing_field_with_mandate(self, timestamp=None):
        if not timestamp:
            timestamp = datetime.now()

        membership_at = (
            OrganizationMembership.objects.active_at(timestamp)
            .filter(member=self, organization__classification="house")
            .order_by("end_time")
            .last()
        )

        if membership_at:
            return membership_at.organization, membership_at.mandate
        else:
            membership_at = (
                OrganizationMembership.objects.filter(
                    member=self, organization__classification="house"
                )
                .order_by("end_time")
                .last()
            )
            if membership_at:
                return membership_at.organization, membership_at.mandate
            else:
                raise NoMembershipException(
                    f"Organization {self.name} {self.id} has no membership in root organization"
                )

    def query_organizations_with_voters(self, timestamp=None):
        if not timestamp:
            timestamp = datetime.now()

        # sometimes we need a list of all parliamentary groups that have voters
        # in a working body, f.e. when calculating unity

        voters_groups_ids = (
            PersonMembership.valid_at(timestamp)
            .filter(organization=self, role="voter")
            .values_list("on_behalf_of", flat=True)
        )

        return Organization.objects.filter(id__in=voters_groups_ids)
