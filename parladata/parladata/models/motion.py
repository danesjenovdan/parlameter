from django.db import models

from parladata.behaviors.models import Parsable, Taggable, Timestampable


class Motion(Timestampable, Taggable, Parsable):
    """Votings which taken place in parlament."""

    datetime = models.DateTimeField(
        blank=True,
        null=True,
        help_text="The date and time when the motion was proposed",
    )

    session = models.ForeignKey(
        "Session",
        blank=True,
        null=True,
        related_name="motions",
        on_delete=models.CASCADE,
        help_text="The legislative session in which the motion was proposed",
    )

    # TODO this should be reworked possibly by allowing organizations as champions
    champions = models.ManyToManyField(
        "Person", help_text="The people who proposed the motion.", blank=True
    )

    summary = models.TextField(blank=True, null=True, help_text="Motion summary")

    text = models.TextField(blank=True, null=True, help_text="The text of the motion")

    classification = models.TextField(
        blank=True, null=True, help_text="Motion classification"
    )

    title = models.TextField(help_text="Title of the motion")

    # TODO rework this into a choice field
    requirement = models.TextField(
        blank=True, null=True, help_text="The requirement for the motion to pass"
    )

    result = models.BooleanField(
        blank=True, null=True, help_text="Did the motion pass?"
    )

    agenda_items = models.ManyToManyField(
        "AgendaItem", blank=True, help_text="Agenda items", related_name="motions"
    )

    law = models.ForeignKey(
        "Law",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="motions",
        help_text="Piece of legislation this motion is about",
    )

    gov_id = models.TextField(
        blank=True, null=True, help_text="Gov ID or identifier for parser"
    )

    def __str__(self):
        return self.title + " --> " + (self.session.name if self.session else "")
