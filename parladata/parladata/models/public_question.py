from django.db import models
from django.utils.translation import gettext_lazy as _
from parladata.behaviors.models import Approvable, Timestampable


class PublicPersonQuestion(Timestampable, Approvable):
    recipient_person = models.ForeignKey(
        "Person",
        verbose_name=_("Person"),
        help_text=_("Recipient person."),
        related_name="received_person_questions",
        on_delete=models.CASCADE,
    )
    author_email = models.EmailField(
        verbose_name=_("author email"),
        help_text=_("Email of the author of the question"),
        max_length=256,
        blank=True,
        null=True,
    )
    text = models.TextField(
        verbose_name=_("text"),
        help_text=_("Text of question"),
    )
    notification_sent_at = models.DateTimeField(
        verbose_name=_("notification sent at"),
        help_text=_("Timestamp when notification was sent"),
        null=True,
        blank=True,
        db_index=True,
    )
    mandate = models.ForeignKey(
        "Mandate",
        verbose_name=_("Mandate"),
        help_text=_("Select the mandate of this public question."),
        blank=True,
        null=True,
        related_name="public_questions",
        on_delete=models.SET_NULL,
    )
    gov_id = models.TextField(
        verbose_name=_("gov_id"),
        help_text=_("Insert the GOV ID."),
        blank=True,
        null=True,
    )

    def __str__(self):
        return f"{self.recipient_person.name} - {self.text[:50]}"

    class Meta:
        verbose_name = _("public person question")
        verbose_name_plural = _("public person questions")


class PublicPersonAnswer(Timestampable, Approvable):
    question = models.ForeignKey(
        "PublicPersonQuestion",
        verbose_name=_("Question"),
        help_text=_("Select the question this answer relates to."),
        on_delete=models.PROTECT,
        related_name="answer",
    )
    text = models.TextField(
        verbose_name=_("text"),
        help_text=_("Text of answer"),
    )
    notification_sent_at = models.DateTimeField(
        verbose_name=_("notification sent at"),
        help_text=_("Timestamp when notification was sent"),
        null=True,
        blank=True,
        db_index=True,
    )
    mandate = models.ForeignKey(
        "Mandate",
        verbose_name=_("Mandate"),
        help_text=_("The mandate of this public question."),
        blank=True,
        null=True,
        related_name="public_answers",
        on_delete=models.SET_NULL,
    )
    gov_id = models.TextField(
        verbose_name=_("gov_id"),
        help_text=_("Gov ID or identifier for parser"),
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = _("public person answer")
        verbose_name_plural = _("public person answers")

    def __str__(self):
        return f"{self.question.recipient_person.name} - {self.text[:50]}"
