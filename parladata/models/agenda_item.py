from django.db import models
from martor.models import MartorField

from parladata.behaviors.models import Taggable, Timestampable


class AgendaItem(Timestampable, Taggable):
    name = models.TextField(blank=True, null=True, help_text="The name of agenda")

    datetime = models.DateTimeField(
        blank=True, null=True, help_text="Date of the item."
    )

    session = models.ForeignKey(
        "Session",
        blank=True,
        null=True,
        related_name="agenda_items",
        on_delete=models.CASCADE,
    )

    order = models.IntegerField(blank=True, null=True, help_text="Order of agenda item")

    gov_id = models.TextField(blank=True, null=True, help_text="gov_id of agenda item")

    text = MartorField(null=True, blank=True, verbose_name="Agenda item content")

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return (self.session.name if self.session else "") + " -> " + self.name
