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
    prompt = models.TextField(
        verbose_name=_("Prompt"),
        help_text=_("The prompt used to generate the summary."),
        blank=True,
        null=True,
    )
    approved_at = models.DateTimeField(
        verbose_name=_("Approved At"),
        help_text=_("The date and time when the summary was approved."),
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = _("Summary")
        verbose_name_plural = _("Summaries")

    def __str__(self):
        return f"Summary for {self.link}"
