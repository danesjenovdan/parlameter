from datetime import datetime

from django.db import models
from django.db.models import OuterRef, Subquery
from django.utils.translation import gettext_lazy as _

from parladata.behaviors.models import (
    Parsable,
    Sluggable,
    Timestampable,
    VersionableFieldsOwner,
)
from parladata.exceptions import NoMembershipException
from parladata.models.memberships import PersonMembership
from parladata.models.versionable_properties import PersonName


class ExtendedManager(models.Manager):
    """
    It's manager that adds values to queryset objects
    """

    def get_queryset(self):
        """
        Subquery create nested select query. In this case query currently valid name of person.
        Query for name is sliced to one obect because you can subquery just a queryset and not a single object.
        Annotation adds inquired name to the person objects.
        """
        latest_name = Subquery(
            PersonName.objects.filter(
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


class Person(Timestampable, Parsable, Sluggable, VersionableFieldsOwner):
    """Model for all people that are somehow connected to the parlament."""

    date_of_birth = models.DateField(
        verbose_name=_("date of birth"),
        help_text=_("Select the date of birth"),
        blank=True,
        null=True,
    )
    date_of_death = models.DateField(
        verbose_name=_("date of death"),
        help_text=_("Select the date of death"),
        blank=True,
        null=True,
    )
    image = models.ImageField(
        verbose_name=_("image (url)"),
        help_text=_("Insert a portrait photograph that focuses on the person's face."),
        blank=True,
        null=True,
    )
    districts = models.ManyToManyField(
        "Area",
        verbose_name=_("Area"),
        help_text=_("Select the person's district"),
        blank=True,
        related_name="candidates",
    )
    # TODO consider this, maybe we don't need it
    active = models.BooleanField(
        verbose_name=_("active"),
        help_text=_("Is this person active?"),
        default=True,
    )

    objects = ExtendedManager()

    @property
    def name(self):
        # just objects in queryset has latest_name attribute
        if hasattr(self, "latest_name"):
            return self.latest_name
        else:
            return self.versionable_property_value_on_date(
                owner=self, property_model_name="PersonName", datetime=datetime.now()
            )

    @property
    def honorific_prefix(self):
        return self.versionable_property_value_on_date(
            owner=self,
            property_model_name="PersonHonorificPrefix",
            datetime=datetime.now(),
        )

    @property
    def honorific_suffix(self):
        return self.versionable_property_value_on_date(
            owner=self,
            property_model_name="PersonHonorificSuffix",
            datetime=datetime.now(),
        )

    @property
    def preferred_pronoun(self):
        return self.versionable_property_value_on_date(
            owner=self,
            property_model_name="PersonPreferredPronoun",
            datetime=datetime.now(),
        )

    @property
    def education(self):
        return self.versionable_property_value_on_date(
            owner=self, property_model_name="PersonEducation", datetime=datetime.now()
        )

    @property
    def education_level(self):
        return self.versionable_property_value_on_date(
            owner=self,
            property_model_name="PersonEducationLevel",
            datetime=datetime.now(),
        )

    @property
    def previous_occupation(self):
        return self.versionable_property_value_on_date(
            owner=self,
            property_model_name="PersonPreviousOccupation",
            datetime=datetime.now(),
        )

    @property
    def number_of_mandates(self):
        return self.versionable_property_value_on_date(
            owner=self,
            property_model_name="PersonNumberOfMandates",
            datetime=datetime.now(),
        )

    @property
    def number_of_voters(self):
        return self.versionable_property_value_on_date(
            owner=self,
            property_model_name="PersonNumberOfVoters",
            datetime=datetime.now(),
        )

    @property
    def email(self):
        return self.versionable_property_value_on_date(
            owner=self, property_model_name="PersonEmail", datetime=datetime.now()
        )

    def parliamentary_group_on_date(self, timestamp=None):
        if not timestamp:
            timestamp = datetime.now()

        active_memberships = PersonMembership.objects.filter(
            models.Q(member=self),
            models.Q(start_time__lte=timestamp) | models.Q(start_time__isnull=True),
            models.Q(end_time__gte=timestamp) | models.Q(end_time__isnull=True),
            models.Q(
                organization__classification="pg"
            ),  # TODO change to parliamentary_group
        )

        if active_memberships.count() > 1:
            # TODO we need a way to bubble these
            # exceptions up to the end user
            raise Exception(
                "\n".join(
                    [
                        f"{active_memberships.count()} active memberships for person {self.id}. Check your data.",
                        f'Membership ids: {list(active_memberships.values_list("id", flat=True))}',
                    ]
                )
            )

        active_membership = active_memberships.first()

        if not active_membership:
            return None

        return active_membership.organization

    def get_last_playing_field_with_mandate(self, timestamp=None):
        if not timestamp:
            timestamp = datetime.now()

        membership_at = (
            PersonMembership.objects.active_at(timestamp)
            .filter(member=self, role="voter", organization__classification="house")
            .order_by("end_time")
            .last()
        )

        if membership_at:
            return membership_at.organization, membership_at.mandate
        else:
            # get leader membership
            membership_at = (
                PersonMembership.objects.active_at(timestamp)
                .filter(member=self, role="leader", organization__classification="root")
                .order_by("end_time")
                .last()
            )

            if membership_at:
                return membership_at.organization, membership_at.mandate
            else:
                membership_at = (
                    PersonMembership.objects.filter(
                        member=self, role="voter", organization__classification="house"
                    )
                    .order_by("end_time")
                    .last()
                )
                if membership_at:
                    return membership_at.organization, membership_at.mandate
                else:
                    raise NoMembershipException(
                        f"Person {self.name} {self.id} has no voter membership in root organization"
                    )

    def __str__(self):
        return f"{self.id}: {self.name}"

    class Meta:
        verbose_name = "Person"
        verbose_name_plural = "People"
