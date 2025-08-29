from django.db import models
from martor.models import MartorField
from django.utils.translation import gettext_lazy as _
from parladata.behaviors.models import Taggable, Timestampable


class AgendaItem(Timestampable, Taggable):
    name = models.TextField(_("Name"), blank=True, null=True, help_text=_("The name of agenda"))

    datetime = models.DateTimeField(
       _("Date and time"), blank=True, null=True, help_text=_("Date of the item.")
    )

    session = models.ForeignKey(
        _("Session"),
        blank=True,
        null=True,
        related_name="agenda_items",
        help_text=_("Select the session.")
        on_delete=models.CASCADE,
    )

    order = models.IntegerField(blank=True, null=True, help_text="Order of agenda item")

    gov_id = models.TextField(_("gov_id"), blank=True, null=True, help_text=_("gov_id the of agenda item"))

    text = MartorField(null=True, blank=True, verbose_name="Agenda item content")

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return (self.session.name if self.session else "") + " -> " + self.name
