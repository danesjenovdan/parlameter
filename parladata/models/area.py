from django.db import models
from django.utils.translation import gettext_lazy as _

from parladata.behaviors.models import Sluggable, Timestampable


class Area(Timestampable, Sluggable):
    """Places of any kind."""

    name = models.TextField(_("name"), help_text=_("Area name"))

    identifier = models.TextField(
        _("identifier"), blank=True, null=True, help_text="Area identifier"
    )

    parent = models.ForeignKey(
        "Area", blank=True, null=True, on_delete=models.CASCADE, help_text="Area parent"
    )

    classification = models.TextField(
        _("classification"),
        blank=True,
        null=True,
        help_text="Area classification (Unit/Region)",
    )

    def __str__(self):
        return self.name
