from django.db import models
from django.utils.translation import gettext_lazy as _

from parladata.behaviors.models import Taggable, Timestampable


# TODO think about this
class Link(Timestampable, Taggable):
    """
    A URL
    # max_length increased to account for lengthy Camera's URLS
    """

    url = models.URLField(_("url"), max_length=350, help_text=_("Insert the URL"))

    note = models.CharField(
        _("note"),
        max_length=256,
        blank=True,
        null=True,
        help_text=_("A note, e.g. 'Wikipedia page'"),
    )

    name = models.TextField(
        _("name"), blank=True, null=True, help_text=_("Name of the link")
    )

    date = models.DateField(
        _("date"), blank=True, null=True, help_text=_("Insert the date")
    )

    session = models.ForeignKey(
        _("Session"),
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        verbose_name=_("Session"),
        related_name="links",
        help_text=_("Select the session"),
    )

    organization = models.ForeignKey(
        _("Organization"),
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        verbose_name=_("Organization"),
        help_text=_("Select the organization connected to the link content"),
        related_name="links",
    )

    person = models.ForeignKey(
        _("Person"),
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        verbose_name=_("Person"),
        help_text=_("Select the person connected to the link"),
        related_name="links",
    )

    membership = models.ForeignKey(
        _("PersonMembership"),
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        verbose_name=_("Person membership"),
        help_text=_("The membership of this link."),
        related_name="links",
    )

    motion = models.ForeignKey(
        _("Motion"),
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        verbose_name=_("Motion"),
        help_text=_("Select the motion this link belongs to."),
        related_name="links",
    )

    question = models.ForeignKey(
        _("Question"),
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        verbose_name=_("Question"),
        help_text=_("Select the question this link belongs to."),
        related_name="links",
    )

    answer = models.ForeignKey(
        _("Answer"),
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        verbose_name=_("Answer"),
        help_text=_("Select the answer this link belongs to."),
        related_name="links",
    )

    legislation_consideration = models.ForeignKey(
        _("LegislationConsideration"),
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        verbose_name=_("Legislation Consideration"),
        help_text=_("The legislation consideration this link belongs to."),
        related_name="links",
    )

    agenda_item = models.ForeignKey(
        _("AgendaItem"),
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        verbose_name=_("Agenda item"),
        help_text=_("Select the agenda item this link belongs to."),
        related_name="links",
    )

    def __str__(self):
        return self.url
