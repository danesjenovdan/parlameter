from django.db import models
from django.utils.translation import gettext_lazy as _

from parladata.behaviors.models import Timestampable


class Amendment(Timestampable):
    """Amendments which are proposed to a motion."""

    uid = models.TextField(
        verbose_name=_("uid"),
        help_text=_("uid reference of the amendment found on the source page"),
        blank=True,
        null=True,
    )
    mandate = models.ForeignKey(
        "Mandate",
        verbose_name=_("Mandate"),
        help_text=_("Select the mandate of the amendment."),
        related_name="amendments",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    abbreviation = models.TextField(
        verbose_name=_("abbreviation"),
        help_text=_("Abbreviation of the amendment"),
        blank=True,
        null=True,
    )
    timestamp = models.DateTimeField(
        verbose_name=_("timestamp"),
        help_text=_("Timestamp of the amendment"),
        blank=True,
        null=True,
    )
    timestamp_vote = models.DateTimeField(
        verbose_name=_("timestamp vote"),
        help_text=_("Timestamp of the vote on the amendment"),
        blank=True,
        null=True,
    )
    procedure_phase = models.ForeignKey(
        "ProcedurePhase",
        verbose_name=_("Procedure phase"),
        help_text=_("The phase of the procedure in which the amendment was proposed"),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    procedure_type = models.ForeignKey(
        "ProcedureType",
        verbose_name=_("Procedure type"),
        help_text=_("The type of the procedure in which the amendment was proposed"),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    motion = models.ForeignKey(
        "Motion",
        verbose_name=_("Motion"),
        help_text=_("The motion to which the amendment is proposed"),
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    legislation = models.ForeignKey(
        "Law",
        verbose_name=_("Legislation"),
        help_text=_("The legislation to which the amendment is proposed"),
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    title = models.TextField(
        verbose_name=_("title"),
        help_text=_("Insert the title of the amendment eg. 'Amendment on...'"),
        blank=True,
        null=True,
    )
    proposer_text = models.TextField(
        verbose_name=_("proposer text"),
        help_text=_("Insert the text of the proposer of the amendment"),
        blank=True,
        null=True,
    )
    proposed_by_organizations = models.ManyToManyField(
        "Organization",
        verbose_name=_("Proposed by"),
        help_text=_("The organization which proposed the amendment"),
        blank=True,
    )
    proposed_by_people = models.ManyToManyField(
        "Person",
        verbose_name=_("Proposed by"),
        help_text=_("The person who proposed the amendment"),
        blank=True,
    )
    explanation = models.TextField(
        verbose_name=_("explanation"),
        help_text=_("Insert the explanation of the amendment"),
        blank=True,
        null=True,
    )
    content = models.TextField(
        verbose_name=_("content"),
        help_text=_("Insert the content of the amendment"),
        blank=True,
        null=True,
    )
    reference = models.TextField(
        verbose_name=_("reference"),
        help_text=_("Insert reference of the amendment"),
        blank=True,
        null=True,
    )
    result = models.ForeignKey(
        "AmendmentResult",
        verbose_name=_("Amendment result"),
        help_text=_("Select the result of the amendment"),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )

    class Meta:
        verbose_name = _("Amendment")
        verbose_name_plural = _("Amendments")


class AmendmentResult(Timestampable):
    name = models.TextField(
        verbose_name=_("Name"),
        help_text=_(
            "Name of the amendment result. For example: 'Accepted', 'Rejected', 'Withdrawn'"
        ),
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Amendment result")
        verbose_name_plural = _("Amendment results")
