from django.db import models
from django.utils.translation import gettext_lazy as _
from parladata.behaviors.models import Parsable, Taggable, Timestampable


class Motion(Timestampable, Taggable, Parsable):
    """Votings which taken place in parlament."""

    datetime = models.DateTimeField(
        _("datetime"),
        blank=True,
        null=True,
        help_text=_("Select the date and time when the motion was proposed"),
    )

    session = models.ForeignKey(
        _("Session"),
        blank=True,
        null=True,
        related_name="motions",
        on_delete=models.CASCADE,
        verbose_name=_("Session"),
        help_text=_("Select the legislative session in which the motion was proposed"),
    )

    # TODO this should be reworked possibly by allowing organizations as champions
    champions = models.ManyToManyField(
        "Person", help_text="The people who proposed the motion.", blank=True
    )

    summary = models.TextField(
        _("summary"), blank=True, null=True, help_text=_("Insert the motion summary")
    )

    text = models.TextField(
        _("text"), blank=True, null=True, help_text=_("Insert the text of the motion")
    )

    classification = models.TextField(
        _("classification"), blank=True, null=True, help_text=_("Motion classification")
    )

    title = models.TextField(
        _("title"), help_text="Insert the title of the motion eg. 'Zakon o...'"
    )

    # TODO rework this into a choice field
    requirement = models.TextField(
        blank=True, null=True, help_text="The requirement for the motion to pass"
    )

    result = models.BooleanField(
        _("result"), blank=True, null=True, help_text=_("Did the motion pass?")
    )

    agenda_items = models.ManyToManyField(
        "AgendaItem",
        blank=True,
        help_text="Agenda items",
        related_name="motions",
        verbose_name=_("Agenda items"),
    )

    law = models.ForeignKey(
        _("Law"),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Law"),
        related_name="motions",
        help_text=_("Select the piece of legislation this motion is about"),
    )

    gov_id = models.TextField(
        blank=True, null=True, help_text="Gov ID or identifier for parser"
    )

    def __str__(self):
        return self.title + " --> " + (self.session.name if self.session else "")
