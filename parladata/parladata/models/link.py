from django.db import models
from django.utils.translation import gettext_lazy as _

from parladata.behaviors.models import Taggable, Timestampable


# TODO think about this
class Link(Timestampable, Taggable):
    """
    A URL
    # max_length increased to account for lengthy Camera's URLS
    """

    url = models.URLField(_("url"), max_length=350, help_text=_("A URL"))

    note = models.CharField(
        _("note"),
        max_length=256,
        blank=True,
        null=True,
        help_text=_("A note, e.g. 'Wikipedia page'"),
    )

    name = models.TextField(blank=True, null=True)

    date = models.DateField(blank=True, null=True)

    session = models.ForeignKey(
        "Session", blank=True, null=True, on_delete=models.CASCADE, related_name="links"
    )

    organization = models.ForeignKey(
        "Organization",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        help_text="The organization of this link.",
        related_name="links",
    )

    person = models.ForeignKey(
        "Person",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        help_text="The person of this link.",
        related_name="links",
    )

    membership = models.ForeignKey(
        "PersonMembership",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        help_text="The membership of this link.",
        related_name="links",
    )

    motion = models.ForeignKey(
        "Motion",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        help_text="The motion of this link.",
        related_name="links",
    )

    question = models.ForeignKey(
        "Question",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        help_text="The question this link belongs to.",
        related_name="links",
    )

    answer = models.ForeignKey(
        "Answer",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        help_text="The answer this link belongs to.",
        related_name="links",
    )

    legislation_consideration = models.ForeignKey(
        "LegislationConsideration",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        help_text="The legislation consideration this link belongs to.",
        related_name="links",
    )

    agenda_item = models.ForeignKey(
        "AgendaItem",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        help_text="The agenda item this link belongs to.",
        related_name="links",
    )

    def __str__(self):
        return self.url
