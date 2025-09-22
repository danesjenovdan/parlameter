from django.db import models
from django.utils.translation import gettext_lazy as _
from martor.models import MartorField

from parladata.behaviors.models import Taggable, Timestampable


class AgendaItem(Timestampable, Taggable):
    name = models.TextField(
        verbose_name=_("Name"),
        help_text=_("The name of agenda"),
        blank=True,
        null=True,
    )
    datetime = models.DateTimeField(
        verbose_name=_("Date and time"),
        help_text=_("Date and time of the item."),
        blank=True,
        null=True,
    )
    session = models.ForeignKey(
        "Session",
        verbose_name=_("Session"),
        help_text=_("Select the session."),
        blank=True,
        null=True,
        related_name="agenda_items",
        on_delete=models.CASCADE,
    )
    order = models.IntegerField(
        verbose_name=_("Order"),
        help_text=_("Order of agenda item"),
        blank=True,
        null=True,
    )
    gov_id = models.TextField(
        verbose_name=_("Government ID"),
        help_text=_("Government ID of the agenda item"),
        blank=True,
        null=True,
    )
    text = MartorField(
        verbose_name=_("Agenda item content"),
        help_text=_("Content of the agenda item in markdown format"),
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _("Agenda item")
        verbose_name_plural = _("Agenda items")
        ordering = ["order"]

    def __str__(self):
        return (self.session.name if self.session else "") + " -> " + self.name
