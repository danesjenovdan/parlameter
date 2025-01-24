from django.db import models

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
        "Mandate",
        blank=False,
        null=False,
        related_name="sessions",
        on_delete=models.CASCADE,
        help_text="The mandate of this session.",
    )

    name = models.TextField(blank=False, null=False, help_text="Session name")

    gov_id = models.TextField(blank=True, null=True, help_text="Gov website ID.")

    start_time = models.DateTimeField(blank=True, null=True, help_text="Start time")

    end_time = models.DateTimeField(blank=True, null=True, help_text="End time")

    organizations = models.ManyToManyField(
        "Organization",
        related_name="sessions",
        help_text="The organization(s) in session",
    )

    classification = models.CharField(
        max_length=128,
        help_text="Session classification",
        choices=CLASSIFICATIONS,
        default="unknown",
    )

    in_review = models.BooleanField(
        default=False, help_text="Is session still in review?"
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
