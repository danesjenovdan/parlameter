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
    start_time = models.DateTimeField(_("start_time"), blank=True, null=True, help_text=_("Select the start time"))

    end_time = models.DateTimeField(_("end_time"), blank=True, null=True, help_text=_("Select the end time"))

    organization = models.ForeignKey(
        _("Organization"),
        blank=False,
        null=False,
        related_name="%(class)ss_children",
        on_delete=models.CASCADE,
        help_text=_("Select the organization that the member belongs to."),
    )

    mandate = models.ForeignKey(
        _("Mandate"),
        blank=True,
        null=True,
        help_text=_("Select the mandate.")
        verbose_name=_("Mandate"),
        related_name="%(class)ss",
        on_delete=models.CASCADE,
    )

    objects = ActiveAtQuerySet.as_manager()

    def __str__(self):
        return f"Member: {self.member}, Org: {self.organization}, StartTime: {self.start_time}"

    class Meta:
        abstract = True


class PersonMembership(Membership):
    """A relationship between a person and an organization."""

    ROLES = [
        ("member", "member"),
        ("deputy member", "deputy member"),
        ("voter", "voter"),
        ("president", "president"),
        ("deputy", "deputy"),
        ("leader", "leader"),
    ]

    member = models.ForeignKey(
        _("Person"),
        blank=False,
        null=False,
        on_delete=models.CASCADE,
        verbose_name= _("Person"),
        related_name="person_memberships",
        help_text=_("Choose the person to whom the membership applies."),
    )

    role = models.TextField(
        _("role"),
        blank=False,
        null=False,
        default="member",
        choices=ROLES,
        verbose_name= _("Role"),
        help_text=_("Select the role that the person fulfills in the organization."),
    )

    on_behalf_of = models.ForeignKey(
        _("Organization"),
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        verbose_name= _("Organization"),
        related_name="representatives",
        help_text=_("Select the organization on whose behalf the person is a member of the organization."),
    )

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
        _("Organization"),
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="organization_memberships",
        verbose_name= _("Organization"),
        help_text=_("The organization that is a party to the relationship"),
    )

    @staticmethod
    def valid_at(timestamp=None):
        if not timestamp:
            timestamp = datetime.now()

        return OrganizationMembership.objects.filter(
            Q(start_time__lte=timestamp) | Q(start_time__isnull=True),
            Q(end_time__gte=timestamp) | Q(end_time__isnull=True),
        )
