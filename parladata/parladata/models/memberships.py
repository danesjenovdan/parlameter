from datetime import datetime

from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from parladata.behaviors.models import Timestampable

# TODO touch parents on save
# TODO touch parents on delete


class ActiveAtQuerySet(models.QuerySet):
    def active_at(self, timestamp):
        return self.filter(
            Q(start_time__lte=timestamp) | Q(start_time__isnull=True),
            Q(end_time__gte=timestamp) | Q(end_time__isnull=True),
        )


class Membership(Timestampable):
    start_time = models.DateTimeField(
        verbose_name=_("start_time"),
        help_text=_("Select the start time"),
        blank=True,
        null=True,
    )
    end_time = models.DateTimeField(
        verbose_name=_("end_time"),
        help_text=_("Select the end time"),
        blank=True,
        null=True,
    )
    organization = models.ForeignKey(
        "Organization",
        verbose_name=_("Organization"),
        help_text=_("Select the organization that the member belongs to."),
        blank=False,
        null=False,
        related_name="%(class)ss_children",
        on_delete=models.CASCADE,
    )
    mandate = models.ForeignKey(
        "Mandate",
        verbose_name=_("Mandate"),
        help_text=_("Select the mandate."),
        blank=True,
        null=True,
        related_name="%(class)ss",
        on_delete=models.CASCADE,
    )

    objects = ActiveAtQuerySet.as_manager()

    class Meta:
        abstract = True
        verbose_name = _("membership")
        verbose_name_plural = _("memberships")

    def __str__(self):
        return f"Member: {self.member}, Org: {self.organization}, StartTime: {self.start_time}"

    


class PersonMembership(Membership):
    """A relationship between a person and an organization."""

    ROLES = [
        ("member", _("member")),
        ("deputy member", _("deputy member")),
        ("voter", _("voter")),
        ("president", _("president")),
        ("deputy", _("deputy")),
        ("leader", _("leader")),
    ]
    member = models.ForeignKey(
        "Person",
        verbose_name=_("Person"),
        help_text=_("Choose the person to whom the membership applies."),
        blank=False,
        null=False,
        on_delete=models.CASCADE,
        related_name="person_memberships",
    )
    role = models.TextField(
        verbose_name=_("Role"),
        help_text=_("Select the role that the person fulfills in the organization."),
        blank=False,
        null=False,
        default="member",
        choices=ROLES,
    )
    on_behalf_of = models.ForeignKey(
        "Organization",
        verbose_name=_("On behalf of organization"),
        help_text=_(
            "Select the organization on whose behalf the person is a member of the organization."
        ),
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="representatives",
    )

    class Meta:
        verbose_name = _("Person Membership")
        verbose_name_plural = _("Person Memberships")

    def __str__(self):
        return f"{self.role}: {self.member}, Org: {self.organization}, StartTime: {self.start_time}"

    @staticmethod
    def valid_at(timestamp):
        return PersonMembership.objects.filter(
            Q(start_time__lte=timestamp) | Q(start_time__isnull=True),
            Q(end_time__gte=timestamp) | Q(end_time__isnull=True),
        )

    @staticmethod
    def valid_before(timestamp):
        return PersonMembership.objects.filter(
            Q(start_time__lte=timestamp) | Q(start_time__isnull=True)
        )

    # after we save a membership we should
    # make sure the actual member (person)
    # updates its updated_at timestamp
    #
    # WARNING!
    # this only works because Person
    # inherits from VersionableFieldsOwner
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.member.touch()


class OrganizationMembership(Membership):
    member = models.ForeignKey(
        "Organization",
        verbose_name=_("Organization"),
        help_text=_("The organization that is a party to the relationship"),
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="organization_memberships",
    )

    class Meta:
        verbose_name = _("Organization Membership")
        verbose_name_plural = _("Organization Memberships")

    @staticmethod
    def valid_at(timestamp=None):
        if not timestamp:
            timestamp = datetime.now()

        return OrganizationMembership.objects.filter(
            Q(start_time__lte=timestamp) | Q(start_time__isnull=True),
            Q(end_time__gte=timestamp) | Q(end_time__isnull=True),
        )
