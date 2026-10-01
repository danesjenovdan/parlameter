from django.db import models
from django.utils.translation import gettext_lazy as _

from parladata.behaviors.models import Timestampable


class Summary(Timestampable):
    """Summary of a law or legislation."""

    text = models.TextField(
        verbose_name=_("Text"),
        help_text=_("The summary text of the law or legislation."),
        blank=True,
        null=True,
    )
    link = models.ForeignKey(
        "Link",
        verbose_name=_("Link"),
        help_text=_("The link associated with the summary."),
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    ai_model = models.TextField(
        verbose_name=_("Model"),
        help_text=_("The AI model associated with the summary."),
        blank=True,
        null=True,
    )
    ai_model_version = models.TextField(
        verbose_name=_("Model Version"),
        help_text=_("The version of the AI model associated with the summary."),
        blank=True,
        null=True,
    )
    is_approved = models.BooleanField(
        verbose_name=_("Is Approved"),
        help_text=_("Indicates whether the summary has been approved."),
        default=False,
    )

    class Meta:
        verbose_name = _("Summary")
        verbose_name_plural = _("Summaries")

    def __str__(self):
        return f"Summary for {self.link}"
