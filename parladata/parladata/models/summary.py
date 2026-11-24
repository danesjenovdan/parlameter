from django.db import models
from django.utils.translation import gettext_lazy as _

from parladata.behaviors.models import Timestampable


class Summary(Timestampable):
    """Summary of a law or legislation."""

    class ERROR(models.TextChoices):
        NONE = "", _("None")
        PARSING_FAILED = "parsing_failed", _("Parsing Failed")

    text = models.TextField(
        verbose_name=_("Text"),
        help_text=_("The summary text of the law or legislation."),
        blank=True,
        null=True,
    )
    links = models.ManyToManyField(
        "Link",
        verbose_name=_("Links"),
        # related_name="summaries",
        help_text=_("The links associated with the summary."),
        blank=True,
    )
    law = models.ForeignKey(
        "Law",
        verbose_name=_("Law"),
        help_text=_("Summary of this law."),
        on_delete=models.CASCADE,
        blank=True,
        null=True,
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
    error = models.CharField(
        verbose_name=_("Error"),
        help_text=_("The error message if the summary generation failed."),
        null=True,
        blank=True,
        choices=ERROR.choices,
        default=ERROR.NONE,
        max_length=1024,
    )

    class Meta:
        verbose_name = _("Summary")
        verbose_name_plural = _("Summaries")

    def __str__(self):
        return f"Summary for {', '.join(str(link) for link in self.links.all())}"
