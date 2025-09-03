from datetime import datetime

from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from parladata.behaviors.models import Timestampable
from parladata.exceptions import NoMembershipException
from parladata.models.memberships import OrganizationMembership, PersonMembership


class ActiveAtQuerySet(models.QuerySet):
    def active_at(self, timestamp):
        return self.filter(
            Q(beginning__lte=timestamp) | Q(beginning__isnull=True),
            Q(ending__gte=timestamp) | Q(ending__isnull=True),
        )


class Mandate(models.Model):
    """Mandate"""

    description = models.TextField(
        verbose_name=_("Description"),
        help_text=_("Description of the mandate"),
        blank=True,
        null=True,
    )
    beginning = models.DateTimeField(
        verbose_name=_("Beginning"),
        help_text=_("Beginning of the mandate"),
        blank=True,
        null=True,
    )

    ending = models.DateTimeField(
        verbose_name=_("Ending"),
        help_text=_("Ending of the mandate"),
        blank=True,
        null=True,
    )
    objects = ActiveAtQuerySet.as_manager()

    class Meta:
        verbose_name = _("Mandate")
        verbose_name_plural = _("Mandates")
        ordering = ["beginning"]

    def query_root_organizations(self, timestamp=None):
        if not timestamp:
            timestamp = datetime.now()

        memberships = OrganizationMembership.valid_at(timestamp).filter(
            mandate=self, member__classification="root"
        )
        if not memberships:
            raise NoMembershipException(
                f"No root organization memberships exist for mandate {self.description}!"
            )
        # raise Exception(f'Multiple root organization memberships exist for this mandate!')

        playing_field = memberships.first().member
        root_organization = memberships.first().organization

        return root_organization, playing_field

    # TODO fix this to use mandate for multiple root organizatuons
    def query_person_root_organization(self, person, timestamp=None):
        if timestamp:
            valid_memberships = PersonMembership.valid_at(timestamp)
        else:
            valid_memberships = PersonMembership.objects.all()

        person_memberships = valid_memberships.filter(
            member=person, organization__classification="root"
        ).first()
        if person_memberships:
            return person_memberships.organization
        else:
            raise Exception("No root organization memberships exist for this person!")

    def __str__(self):
        return self.description

    def get_time_range_from_mandate(self, to_timestamp):
        if self.beginning:
            from_timestamp = self.beginning
        else:
            from_timestamp = datetime.min
        if not to_timestamp:
            to_timestamp = datetime.now()
        if self.ending and self.ending < to_timestamp:
            to_timestamp = self.ending

        return from_timestamp, to_timestamp

    @classmethod
    def get_active_mandate_at(cls, timestamp):
        mandate = Mandate.objects.active_at(timestamp).first()
        if mandate:
            return mandate
        else:
            raise Exception("There's no mandate for the given timestamp")


class EducationLevel(Timestampable):
    text = models.TextField()
    order = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.text

    class Meta(object):
        ordering = ["order"]
