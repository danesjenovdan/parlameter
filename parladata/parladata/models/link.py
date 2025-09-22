from django.db import models
from django.utils.translation import gettext_lazy as _

from parladata.behaviors.models import Taggable, Timestampable


# TODO think about this
class Link(Timestampable, Taggable):
    """
    A URL
    # max_length increased to account for lengthy Camera's URLS
    """

    url = models.URLField(
        verbose_name=_("url"),
        help_text=_("Insert the URL"),
        max_length=350,
    )
    note = models.CharField(
        verbose_name=_("note"),
        help_text=_("A note, e.g. 'Wikipedia page'"),
        max_length=256,
        blank=True,
        null=True,
    )
    name = models.TextField(
        verbose_name=_("name"),
        help_text=_("Name of the link"),
        blank=True,
        null=True,
    )
    date = models.DateField(
        verbose_name=_("date"),
        help_text=_("Insert the date"),
        blank=True,
        null=True,
    )
    session = models.ForeignKey(
        "Session",
        verbose_name=_("Session"),
        help_text=_("Select the session"),
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="links",
    )
    organization = models.ForeignKey(
        "Organization",
        verbose_name=_("Organization"),
        help_text=_("Select the organization connected to the link content"),
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="links",
    )
    person = models.ForeignKey(
        "Person",
        verbose_name=_("Person"),
        help_text=_("Select the person connected to the link"),
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="links",
    )
    membership = models.ForeignKey(
        "PersonMembership",
        verbose_name=_("Person membership"),
        help_text=_("The membership of this link."),
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="links",
    )
    motion = models.ForeignKey(
        "Motion",
        verbose_name=_("Motion"),
        help_text=_("Select the motion this link belongs to."),
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="links",
    )
    question = models.ForeignKey(
        "Question",
        verbose_name=_("Question"),
        help_text=_("Select the question this link belongs to."),
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="links",
    )
    answer = models.ForeignKey(
        "Answer",
        verbose_name=_("Answer"),
        help_text=_("Select the answer this link belongs to."),
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="links",
    )
    legislation_consideration = models.ForeignKey(
        "LegislationConsideration",
        verbose_name=_("Legislation Consideration"),
        help_text=_("The legislation consideration this link belongs to."),
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="links",
    )
    agenda_item = models.ForeignKey(
        "AgendaItem",
        verbose_name=_("Agenda item"),
        help_text=_("Select the agenda item this link belongs to."),
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="links",
    )

    class Meta:
        verbose_name = _("link")
        verbose_name_plural = _("links")
        # ordering = ['-created_at']

    def __str__(self):
        return self.url
