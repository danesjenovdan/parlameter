from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from parladata.behaviors.models import Timestampable


class Ballot(Timestampable):
    """All ballots from all votes."""

    OPTIONS = [
        ("for", _("for")),
        ("against", _("against")),
        ("abstain", _("abstain")),
        ("absent", _("absent")),
        # following is a special case for slovenian
        # municipalities there are situations where
        # they check if they have a majority of yeses
        # and if they do they don't ask anyone else
        # if they are against or abstained
        ("did not vote", _("did not vote")),
    ]

    vote = models.ForeignKey(
        "Vote",
        verbose_name=_("Vote"),
        help_text=_("What was the vote on"),
        related_name="ballots",
        on_delete=models.CASCADE,
    )
    personvoter = models.ForeignKey(
        "Person",
        verbose_name=_("Person"),
        help_text=_("Who voted"),
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="ballots",
    )
    orgvoter = models.ForeignKey(
        "Organization",
        verbose_name=_("Organization"),
        help_text=_("Which organization voted"),
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="ballots",
    )
    option = models.CharField(
        verbose_name=_("Option"),
        help_text=_("Choose one of the possible options"),
        blank=True,
        null=True,
        max_length=128,
        choices=OPTIONS,
    )

    class Meta:
        verbose_name = _("Ballot")
        verbose_name_plural = _("Ballots")

    def __str__(self):
        if self.personvoter and self.orgvoter:
            raise Exception(
                f"Both personvoter and orgvoter are set for this ballot (id {self.id}). Something is wrong with your data, this should never happen."
            )

        if self.personvoter:
            return self.personvoter.name

        if self.orgvoter:
            return self.orgvoter.name

        return "Anonymous ballot"

    def clean(self):
        if self.personvoter and self.orgvoter:
            raise ValidationError(
                "The ballot should have only one of personvoter or orgvoter filled field."
            )
