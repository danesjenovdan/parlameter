from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand, CommandError
from taggit.models import Tag

from parlacards.models import GroupTfidf, PersonTfidf, SessionTfidf
from parladata.models import (
    AgendaItem,
    Area,
    Ballot,
    Document,
    Law,
    Link,
    Mandate,
    Motion,
    Organization,
    OrganizationMembership,
    Person,
    PersonMembership,
    Question,
    Session,
    Speech,
    Vote,
)
from parladata.models.common import EducationLevel
from parladata.models.versionable_properties import (
    OrganizationAcronym,
    OrganizationEmail,
    OrganizationName,
    PersonEducation,
    PersonEducationLevel,
    PersonEmail,
    PersonName,
    PersonNumberOfMandates,
    PersonNumberOfPoints,
    PersonNumberOfVoters,
    PersonPreferredPronoun,
    PersonPreviousOccupation,
)


class Command(BaseCommand):
    help = "Set motion tags"

    def handle(self, *args, **options):
        self.stdout.write("Creating editor group")

        self.basc_options = [("change_", "Can change "), ("view_", "Can view ")]
        self.options = [
            ("add_", "Can add "),
            ("change_", "Can change "),
            ("view_", "Can view "),
            ("delete_", "Can delete "),
        ]

        models = [
            Motion,
            Vote,
            Organization,
            OrganizationMembership,
            Person,
            Session,
            PersonPreviousOccupation,
            PersonName,
            PersonEducation,
            PersonNumberOfMandates,
            PersonEmail,
            PersonPreferredPronoun,
            PersonNumberOfVoters,
            PersonNumberOfPoints,
            OrganizationName,
            OrganizationEmail,
            OrganizationAcronym,
            PersonTfidf,
            GroupTfidf,
            SessionTfidf,
            Area,
            Law,
            Link,
            Mandate,
            PersonEducationLevel,
            PersonMembership,
            Speech,
            Tag,
            AgendaItem,
            Ballot,
            Question,
            Document,
            EducationLevel,
        ]

        editor, created = Group.objects.get_or_create(name="editor")

        for model in models:
            print(model)
            ct = ContentType.objects.get_for_model(model)
            permissions = self.get_permissions(model.__name__.lower(), ct, self.options)
            editor.permissions.add(*permissions)

    def get_permissions(self, name, ct, options):
        permissions = []
        for option in options:
            print(f"{option[0]}{name}")
            permissions.append(
                Permission.objects.get(
                    content_type_id=ct.id, codename=f"{option[0]}{name}"
                )
            )
        return permissions
