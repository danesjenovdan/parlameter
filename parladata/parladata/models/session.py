from django.db import models
from django.utils.translation import gettext_lazy as _

from parladata.behaviors.models import Timestampable


class Session(Timestampable):
    """Sessions that happened in parliament."""

    CLASSIFICATIONS = [
        ("unknown", _("unknown")),
        ("regular", _("regular")),
        ("irregular", _("irregular")),
        ("correspondent", _("correspondent")),
        ("urgent", _("urgent")),
    ]
    mandate = models.ForeignKey(
        "Mandate",
        verbose_name=_("Mandate"),
        help_text=_("Select the mandate of this session."),
        blank=False,
        null=False,
        related_name="sessions",
        on_delete=models.CASCADE,
    )
    name = models.TextField(
        verbose_name=_("name"),
        help_text=_("Insert the session name and number e.g. '48. nujna seja'"),
        blank=False,
        null=False,
    )
    gov_id = models.TextField(
        verbose_name=_("gov_id"),
        help_text=_("Insert the gov website ID."),
        blank=True,
        null=True,
    )
    start_time = models.DateTimeField(
        verbose_name=_("start_time"),
        help_text=_("Insert the start time"),
        blank=True,
        null=True,
    )
    end_time = models.DateTimeField(
        verbose_name=_("end_time"),
        help_text=_("Insert the end time"),
        blank=True,
        null=True,
    )
    organizations = models.ManyToManyField(
        "Organization",
        verbose_name=_("organizations"),
        help_text=_("Select the organization(s) that participated in the session."),
        related_name="sessions",
        through="SessionOrganizationThrough",
    )
    classification = models.CharField(
        verbose_name=_("classification"),
        help_text=_("Select the session classification"),
        max_length=128,
        choices=CLASSIFICATIONS,
        default="unknown",
    )
    in_review = models.BooleanField(
        verbose_name=_("in_review"),
        help_text=_("Is session still in review?"),
        default=False,
    )
    needs_editing = models.BooleanField(
        verbose_name=_("needs_editing"),
        help_text=_("Does this session need editing?"),
        default=False,
    )
    is_joint_session = models.BooleanField(
        verbose_name=_("is_joint_session"),
        help_text=_("Is this a joint session of multiple organizations?"),
        default=False,
    )

    class Meta:
        verbose_name = _("session")
        verbose_name_plural = _("sessions")

    @property
    def organization(self):
        # if self.organizations.all().count() > 1:
        #     raise Exception(
        #         'This session belongs to multiple organizations. Use the plural form "organizations".'
        #     )

        return self.organizations.first()

    def get_joint_name(self):
        if self.is_joint_session:
            return " - ".join(
                self.session_organization_through.all()
                .order_by("id")
                .values_list("name", flat=True)
            )
        else:
            return self.name

    def get_joint_name_with_orgs(self):
        if self.is_joint_session:
            parts = []
            for sot in self.session_organization_through.all().order_by("id"):
                parts.append(f"{sot.organization.name}: {sot.name}")
            return " | ".join(parts)
        else:
            return self.name

    def __str__(self):
        if self.is_joint_session:
            return f"{self.get_joint_name_with_orgs()},  {self.mandate}"
        else:
            org = self.organizations.first()
            if org:
                return f"{self.name}, ({org.name}) {self.mandate}"
            return f"{self.name}, {self.mandate}"


class SessionOrganizationThrough(models.Model):
    session = models.ForeignKey(
        "Session",
        on_delete=models.CASCADE,
        related_name="session_organization_through",
        verbose_name=_("session"),
        help_text=_("Select the session associated with the organization"),
    )
    organization = models.ForeignKey(
        "Organization",
        on_delete=models.CASCADE,
        related_name="session_organization_through",
        verbose_name=_("organization"),
        help_text=_("Select the organization associated with the session"),
    )
    name = models.TextField(
        verbose_name=_("name"),
        help_text=_("Insert the session name and number e.g. '48. nujna seja'"),
        blank=True,
        null=True,
    )

    class Meta:
        db_table = "parladata_session_organizations"
        unique_together = (("session", "organization"),)

    def __str__(self):
        return f"{self.session} - {self.organization} - {self.name}"
