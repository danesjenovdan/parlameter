from django.db import models
from django.utils.translation import gettext_lazy as _

from parladata.behaviors.models import Taggable, Timestampable


class Document(Timestampable, Taggable):
    file = models.FileField(
        verbose_name=_("File"),
        help_text=_("Upload a document file"),
    )
    name = models.TextField(
        verbose_name=_("Name"),
        help_text=_("Name of the document"),
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = _("Document")
        verbose_name_plural = _("Documents")
        ordering = ["id"]

    def __str__(self):
        return self.name
