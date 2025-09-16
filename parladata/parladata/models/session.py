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

    class Meta:
        verbose_name = _("session")
        verbose_name_plural = _("sessions")

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
