from django.db import models
from django.utils.translation import gettext_lazy as _

from parladata.behaviors.models import VersionableProperty
from parladata.models.common import EducationLevel


class PersonVersionableProperty(VersionableProperty):
    owner = models.ForeignKey(
        "parladata.Person",
        verbose_name="Person",
        help_text="Select the person",
        related_name="%(class)s",
        on_delete=models.CASCADE,
    )

    class Meta:
        abstract = True


class PersonName(PersonVersionableProperty):
    class Meta:
        verbose_name = _("Person name")
        verbose_name_plural = _("Person names")


class PersonHonorificPrefix(PersonVersionableProperty):
    class Meta:
        verbose_name = _("Person honorific prefix")
        verbose_name_plural = _("Person honorific prefixes")


class PersonHonorificSuffix(PersonVersionableProperty):
    class Meta:
        verbose_name = _("Person honorific suffix")
        verbose_name_plural = _("Person honorific suffixes")


class PersonPreviousOccupation(PersonVersionableProperty):
    class Meta:
        verbose_name = _("Person previous occupation")
        verbose_name_plural = _("Person previous occupations")


class PersonEducation(PersonVersionableProperty):
    class Meta:
        verbose_name = _("Person education")
        verbose_name_plural = _("Person educations")


class PersonEducationLevel(PersonVersionableProperty):
    education_level = models.ForeignKey(
        EducationLevel,
        verbose_name=_("Education level"),
        help_text=_("Select the education level"),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _("Person education level")
        verbose_name_plural = _("Person education levels")

    @property
    def value(self):
        return self.education_level.text if self.education_level else None


class PersonNumberOfMandates(PersonVersionableProperty):
    value = models.IntegerField(
        verbose_name=_("Number of mandates"),
        help_text=_("Enter the number of mandates"),
        blank=False,
        null=False,
    )

    class Meta:
        verbose_name = _("Person number of mandates")
        verbose_name_plural = _("Person number of mandates")


class PersonEmail(PersonVersionableProperty):
    class Meta:
        verbose_name = _("Person email")
        verbose_name_plural = _("Person emails")


class PersonPreferredPronoun(PersonVersionableProperty):
    PRONOUNS = [
        ("he", _("he")),
        ("she", _("she")),
        ("they", _("they")),
    ]
    value = models.TextField(
        verbose_name=_("Preferred pronoun"),
        help_text=_("Select the preferred pronoun"),
        blank=False,
        null=False,
        choices=PRONOUNS,
    )

    class Meta:
        verbose_name = _("Person preferred pronoun")
        verbose_name_plural = _("Person preferred pronouns")


class PersonNumberOfVoters(PersonVersionableProperty):
    value = models.IntegerField(
        verbose_name=_("Number of voters"),
        help_text=_("Enter the number of voters"),
        blank=False,
        null=False,
    )

    class Meta:
        verbose_name = _("Person number of voters")
        verbose_name_plural = _("Person number of voters")


class PersonNumberOfPoints(PersonVersionableProperty):
    value = models.IntegerField(
        verbose_name=_("Number of points"),
        help_text=_("Enter the number of points"),
        blank=False,
        null=False,
    )

    class Meta:
        verbose_name = _("Person number of points")
        verbose_name_plural = _("Person number of points")


# ORGANIZATION


class OrganizationVersionableProperty(VersionableProperty):
    owner = models.ForeignKey(
        "parladata.Organization",
        verbose_name=_("Owner"),
        help_text=_("Select the organization"),
        related_name="%(class)s",
        on_delete=models.CASCADE,
    )

    class Meta:
        abstract = True


class OrganizationName(OrganizationVersionableProperty):
    class Meta:
        verbose_name = _("Organization name")
        verbose_name_plural = _("Organization names")


class OrganizationAcronym(OrganizationVersionableProperty):
    class Meta:
        verbose_name = _("Organization acronym")
        verbose_name_plural = _("Organization acronyms")


class OrganizationEmail(OrganizationVersionableProperty):
    class Meta:
        verbose_name = _("Organization email")
        verbose_name_plural = _("Organization emails")
