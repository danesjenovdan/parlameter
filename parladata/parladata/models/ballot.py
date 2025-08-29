from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from parladata.behaviors.models import Timestampable


class Ballot(Timestampable):
    """All ballots from all votes."""

    OPTIONS = [
        ("for", "for"),
        ("against", "against"),
        ("abstain", "abstain"),
        ("absent", "absent"),
        # following is a special case for slovenian
        # municipalities there are situations where
        # they check if they have a majority of yeses
        # and if they do they don't ask anyone else
        # if they are against or abstained
        ("did not vote", "did not vote"),
    ]

    vote = models.ForeignKey(
        _("Vote"),
        verbose_name=_("Vote"),
        help_text=_("What was the vote on"),
        related_name="ballots",
        on_delete=models.CASCADE,
    )

    personvoter = models.ForeignKey(
        _("Person"),
        blank=True,
        null=True,
        verbose_name=_("Person"),
        on_delete=models.CASCADE,
        related_name="ballots",
        help_text=_("Who voted"),
    )

    orgvoter = models.ForeignKey(
        _("Organization"),
        blank=True,
        null=True,
        verbose_name=_("Organization"),
        on_delete=models.CASCADE,
        help_text=_("The organization that the voter represents"),
    )

    option = models.CharField(
        _("Option"),
        max_length=128,
        blank=True,
        null=True,
        help_text=_("Choose one of the possible options"),
        choices=OPTIONS,
    )

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
