from django.db import models
from django.utils.translation import gettext_lazy as _

from parladata.behaviors.models import Timestampable


class Medium(Timestampable):
    name = models.TextField(
        verbose_name=_("name"),
        help_text=_("Medium name"),
    )
    url = models.URLField(
        verbose_name=_("url"),
        help_text=_("Medium URL"),
        max_length=255,
    )
    uri = models.TextField(
        verbose_name=_("uri"),
        help_text=_("Medium URI"),
        db_index=True,
    )
    active = models.BooleanField(
        verbose_name=_("active"),
        help_text=_("Is this medium active?"),
        default=True,
    )
    order = models.PositiveIntegerField(
        verbose_name=_("order"),
        help_text=_("Order of appearance"),
        default=1
    )

    class Meta(object):
        verbose_name = _("medium")
        verbose_name_plural = _("media")
        ordering = ["order"]

    def __str__(self):
        return self.name


class MediaReport(Timestampable):
    title = models.TextField(
        verbose_name=_("title"),
        help_text=_("Report title"),
    )
    url = models.URLField(
        verbose_name=_("url"),
        help_text=_("Report URL"),
        max_length=500,
    )
    uri = models.TextField(
        verbose_name=_("uri"),
        help_text=_("Article URI"),
        db_index=True,
    )
    report_date = models.DateField(
        verbose_name=_("report date"),
        help_text=_("Date of the report"),
    )
    retrieval_date = models.DateTimeField(
        verbose_name=_("retrieval date"),
        help_text=_("Date when the report was retrieved"),
        auto_now=True
    )
    medium = models.ForeignKey(
        Medium,
        verbose_name=_("medium"),
        help_text=_("The medium this report is associated with"),
        on_delete=models.CASCADE,
        related_name="reports",
    )
    mentioned_people = models.ManyToManyField(
        "Person",
        verbose_name=_("mentioned people"),
        help_text=_("People mentioned in the report"),
        blank=True,
        related_name="media_reports",
    )
    mentioned_organizations = models.ManyToManyField(
        "Organization",
        verbose_name=_("mentioned organizations"),
        help_text=_("Organizations mentioned in the report"),
        blank=True,
        related_name="media_reports",
    )
    mentioned_legislation = models.ManyToManyField(
        "Law",
        blank=True,
        related_name="media_reports",
    )
    mentioned_motions = models.ManyToManyField(
        "Motion",
        verbose_name=_("mentioned motions"),
        help_text=_("Motions mentioned in the report"),
        blank=True,
        related_name="media_reports",
    )
    mentioned_votes = models.ManyToManyField(
        "Vote",
        verbose_name=_("mentioned votes"),
        help_text=_("Votes mentioned in the report"),
        blank=True,
        related_name="media_reports",
    )

    class Meta(object):
        verbose_name = _("media report")
        verbose_name_plural = _("media reports")

    def __str__(self):
        return self.title
