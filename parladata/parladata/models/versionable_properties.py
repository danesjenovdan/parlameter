from django.db import models

from parladata.behaviors.models import VersionableProperty
from parladata.models.common import EducationLevel


class PersonVersionableProperty(VersionableProperty):
    owner = models.ForeignKey(
        "parladata.Person", related_name="%(class)s", on_delete=models.CASCADE
    )

    class Meta:
        abstract = True


class PersonName(PersonVersionableProperty):
    pass


class PersonHonorificPrefix(PersonVersionableProperty):
    pass


class PersonHonorificSuffix(PersonVersionableProperty):
    pass


class PersonPreviousOccupation(PersonVersionableProperty):
    pass


class PersonEducation(PersonVersionableProperty):
    pass


class PersonEducationLevel(PersonVersionableProperty):
    education_level = models.ForeignKey(
        EducationLevel,
        verbose_name="Education level",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    @property
    def value(self):
        return self.education_level.text if self.education_level else None


class PersonNumberOfMandates(PersonVersionableProperty):
    value = models.IntegerField(blank=False, null=False)


class PersonEmail(PersonVersionableProperty):
    pass


class PersonPreferredPronoun(PersonVersionableProperty):
    PRONOUNS = [
        ("he", "he"),
        ("she", "she"),
        ("they", "they"),
    ]
    value = models.TextField(blank=False, null=False, choices=PRONOUNS)


class PersonNumberOfVoters(PersonVersionableProperty):
    value = models.IntegerField(blank=False, null=False)


class PersonNumberOfPoints(PersonVersionableProperty):
    value = models.IntegerField(blank=False, null=False)


# ORGANIZATION


class OrganizationVersionableProperty(VersionableProperty):
    owner = models.ForeignKey(
        "parladata.Organization", related_name="%(class)s", on_delete=models.CASCADE
    )

    class Meta:
        abstract = True


class OrganizationName(OrganizationVersionableProperty):
    pass


class OrganizationAcronym(OrganizationVersionableProperty):
    pass


class OrganizationEmail(OrganizationVersionableProperty):
    pass
