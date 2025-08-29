from django.db import models
from django.utils.translation import gettext_lazy as _
from parladata.behaviors.models import Timestampable


class Session(Timestampable):
    """Sessions that happened in parliament."""

    CLASSIFICATIONS = [
        ("unknown", "unknown"),
        ("regular", "regular"),
        ("irregular", "irregular"),
        ("correspondent", "correspondent"),
        ("urgent", "urgent"),
    ]

    mandate = models.ForeignKey(
        _("Mandate"),
        blank=False,
        null=False,
        related_name="sessions",
        on_delete=models.CASCADE,
        help_text=_("Select the mandate of this session."),
    )

    name = models.TextField(
        _("name"),
        blank=False,
        null=False,
        help_text=_("Insert the session name and number e.g. '48. nujna seja'"),
    )

    gov_id = models.TextField(
        _("gov_id"), blank=True, null=True, help_text=_("Insert the gov website ID.")
    )

    start_time = models.DateTimeField(
        _("start_time"), blank=True, null=True, help_text=_("Insert the start time")
    )

    end_time = models.DateTimeField(
        _("end_time"), blank=True, null=True, help_text=_("Insert the end time")
    )

    organizations = models.ManyToManyField(
        "Organization",
        related_name="sessions",
        help_text=_("Select the organization(s) that participated in the session."),
    )

    classification = models.CharField(
        _("classification"),
        max_length=128,
        help_text=_("Select the session classification"),
        choices=CLASSIFICATIONS,
        default="unknown",
    )

    in_review = models.BooleanField(
        _("in_review"), default=False, help_text=_("Is session still in review?")
    )

    needs_editing = models.BooleanField("Session needs editing", default=False)

    @property
    def organization(self):
        if self.organizations.all().count() > 1:
            raise Exception(
                'This session belongs to multiple organizations. Use the plural form "organizations".'
            )

        return self.organizations.first()

    def __str__(self):
        if self and self.organization:
            return f"{self.name},  {self.organization.name}, {self.mandate}"
        else:
            return f"{self.name}, {self.mandate}"
