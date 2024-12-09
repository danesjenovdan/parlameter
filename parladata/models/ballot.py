from django.core.exceptions import ValidationError
from django.db import models

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
        "Vote",
        help_text="The vote event",
        related_name="ballots",
        on_delete=models.CASCADE,
    )

    personvoter = models.ForeignKey(
        "Person",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="ballots",
        help_text="The voter",
    )

    orgvoter = models.ForeignKey(
        "Organization",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        help_text="The voter represents and organisation.",
    )

    option = models.CharField(
        max_length=128,
        blank=True,
        null=True,
        help_text="Yes, no, abstain",
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
