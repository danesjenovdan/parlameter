from django.db import models
from django.utils.translation import gettext_lazy as _
from parladata.behaviors.models import Parsable, Taggable, Timestampable


class Motion(Timestampable, Taggable, Parsable):
    """Votings which taken place in parlament."""

    datetime = models.DateTimeField(
        verbose_name=_("datetime"),
        help_text=_("Select the date and time when the motion was proposed"),
        blank=True,
        null=True,
    )
    session = models.ForeignKey(
        "Session",
        verbose_name=_("Session"),
        help_text=_("Select the legislative session in which the motion was proposed"),
        blank=True,
        null=True,
        related_name="motions",
        on_delete=models.CASCADE,
    )
    # TODO this should be reworked possibly by allowing organizations as champions
    champions = models.ManyToManyField(
        "Person",
        verbose_name=_("champions"),
        help_text="The people who proposed the motion.",
        blank=True,
    )
    summary = models.TextField(
        verbose_name=_("summary"),
        help_text=_("Insert the motion summary"),
        blank=True,
        null=True,
    )
    text = models.TextField(
        verbose_name=_("text"),
        help_text=_("Insert the text of the motion"),
        blank=True,
        null=True,
    )
    classification = models.TextField(
        verbose_name=_("classification"),
        help_text=_("Motion classification"),
        blank=True,
        null=True,
    )
    title = models.TextField(
        verbose_name=_("title"),
        help_text="Insert the title of the motion eg. 'Zakon o...'",
    )
    # TODO rework this into a choice field
    requirement = models.TextField(
        verbose_name=_("requirement"),
        help_text="The requirement for the motion to pass",
        blank=True,
        null=True,
    )
    result = models.BooleanField(
        verbose_name=_("result"),
        help_text=_("Did the motion pass?"),
        blank=True,
        null=True,
    )
    agenda_items = models.ManyToManyField(
        "AgendaItem",
        verbose_name=_("Agenda items"),
        help_text=_("Agenda items"),
        blank=True,
        related_name="motions",
    )
    law = models.ForeignKey(
        "Law",
        verbose_name=_("Law"),
        help_text=_("Select the piece of legislation this motion is about"),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="motions",
    )
    gov_id = models.TextField(
        verbose_name=_("Gov ID"),
        help_text=_("Gov ID or identifier for parser"),
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = _("motion")
        verbose_name_plural = _("motions")

    def __str__(self):
        return self.title + " --> " + (self.session.name if self.session else "")
