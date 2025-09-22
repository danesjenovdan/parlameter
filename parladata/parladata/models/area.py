from django.db import models
from django.utils.translation import gettext_lazy as _

from parladata.behaviors.models import Sluggable, Timestampable


class Area(Timestampable, Sluggable):
    """Places of any kind."""

    name = models.TextField(
        verbose_name=_("name"),
        help_text=_("Name of the area"),
    )
    identifier = models.TextField(
        verbose_name=_("Identifier"),
        blank=True,
        null=True,
        help_text=_("Area identifier"),
    )
    parent = models.ForeignKey(
        "Area",
        verbose_name=_("Parent"),
        help_text=_("Select the parent area"),
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    classification = models.TextField(
        verbose_name=_("Classification"),
        help_text=_("Area classification (Unit or Region)"),
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = _("Area")
        verbose_name_plural = _("Areas")

    def __str__(self):
        return self.name
