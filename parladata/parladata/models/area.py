from django.db import models
from django.utils.translation import gettext_lazy as _

from parladata.behaviors.models import Sluggable, Timestampable


class Area(Timestampable, Sluggable):
    """Places of any kind."""

    name = models.TextField(_("name"), help_text=_("Name of the area"))

    identifier = models.TextField(
        _("identifier"), blank=True, null=True, help_text=_("Area identifier")
    )

    parent = models.ForeignKey(
        _("Area"), blank=True, null=True, on_delete=models.CASCADE, help_text=_("Area parent")
    )

    classification = models.TextField(
        _("classification"),
        blank=True,
        null=True,
        help_text=_("Area classification (Unit or Region)"),
    )

    def __str__(self):
        return self.name
