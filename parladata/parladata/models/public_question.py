from django.db import models
from django.utils.translation import gettext_lazy as _
from parladata.behaviors.models import Approvable, Timestampable


class PublicPersonQuestion(Timestampable, Approvable):
    recipient_person = models.ForeignKey(
        _("Person"),
        help_text="Recipient person.",
        related_name="received_person_questions",
        verbose_name=_("Person"),
        on_delete=models.CASCADE,
    )
    author_email = models.EmailField(max_length=256, blank=True, null=True)
    text = models.TextField(help_text="Text of question")
    notification_sent_at = models.DateTimeField(null=True, blank=True, db_index=True)
    mandate = models.ForeignKey(
        _("Mandate"),
        blank=True,
        null=True,
        related_name="public_questions",
        on_delete=models.SET_NULL,
        verbose_name=_("Mandate"),
        help_text=_("Select the mandate of this public question."),
    )
    gov_id = models.TextField(
        _("gov_id"), blank=True, null=True, help_text=_("Insert the GOV ID.")
    )

    def __str__(self):
        return f"{self.recipient_person.name} - {self.text[:50]}"


class PublicPersonAnswer(Timestampable, Approvable):
    question = models.ForeignKey(
        "PublicPersonQuestion",
        on_delete=models.PROTECT,
        related_name="answer",
        verbose_name=_("Question"),
    )
    text = models.TextField(help_text="Text of answer")
    notification_sent_at = models.DateTimeField(null=True, blank=True, db_index=True)
    mandate = models.ForeignKey(
        "Mandate",
        blank=True,
        null=True,
        related_name="public_answers",
        on_delete=models.SET_NULL,
        verbose_name=_("Mandate"),
        help_text="The mandate of this public question.",
    )
    gov_id = models.TextField(
        blank=True, null=True, help_text="Gov ID or identifier for parser"
    )

    def __str__(self):
        return f"{self.question.recipient_person.name} - {self.text[:50]}"
