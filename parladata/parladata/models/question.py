from django.db import models
from django.utils.translation import gettext_lazy as _

from parladata.behaviors.models import Timestampable

QUESTION_TYPES = [
    ("question", _("question")),
    ("initiative", _("initiative")),
    ("unknown", _("unknown")),
]


class Question(Timestampable):
    """All questions from members of parlament."""

    session = models.ForeignKey(
        "Session",
        verbose_name=_("session"),
        help_text=_("The session this question belongs to."),
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )

    mandate = models.ForeignKey(
        "Mandate",
        verbose_name=_("mandate"),
        help_text=_("The mandate of this question."),
        blank=True,
        null=True,
        related_name="questions",
        on_delete=models.SET_NULL,
    )

    timestamp = models.DateTimeField(
        verbose_name=_("date of the question."),
        help_text=_("Date of the question."),
        blank=True,
        null=True,
    )

    answer_timestamp = models.DateTimeField(
        verbose_name=_("date of the answer."),
        help_text=_("Date of answer the question."),
        blank=True,
        null=True,
    )

    title = models.TextField(
        verbose_name=_("title"),
        help_text=_("Title name as written on dz-rs.si"),
        blank=True,
        null=True,
    )

    person_authors = models.ManyToManyField(
        "Person",
        verbose_name=_("authors"),
        help_text=_("The persons (MP) who asked the question."),
        blank=True,
        related_name="authored_questions",
    )

    organization_authors = models.ManyToManyField(
        "Organization",
        verbose_name=_("organization authors"),
        help_text=_("The organizations who asked the question."),
        blank=True,
        related_name="questions_org_author",
    )

    recipient_people = models.ManyToManyField(
        "Person",
        verbose_name=_("recipient people"),
        help_text=_("Recipient person (if it's a person)."),
        blank=True,
        related_name="received_questions",
    )

    recipient_organizations = models.ManyToManyField(
        "Organization",
        verbose_name=_("recipient organizations"),
        help_text=_("Recipient organization (if it's an organization)."),
        blank=True,
        related_name="questions_org",
    )

    recipient_text = models.TextField(
        verbose_name=_("recipient name"),
        help_text=_("Recipient name as written on dz-rs.si"),
        blank=True,
        null=True,
    )

    type_of_question = models.TextField(
        verbose_name=_("type of question"),
        help_text=_("Type of question."),
        blank=True,
        null=True,
        choices=QUESTION_TYPES,
    )

    gov_id = models.TextField(
        verbose_name=_("government ID"),
        help_text=_("Unique identifier of question on government site."),
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = _("question")
        verbose_name_plural = _("questions")

    def __str__(self):
        person_author_names = " ".join(
            [author.name for author in self.person_authors.all()]
        )
        organization_author_names = " ".join(
            [author.name for author in self.organization_authors.all()]
        )
        author = (
            person_author_names if person_author_names else organization_author_names
        )
        return f"{self.type_of_question}: {self.title} - {author}"


class Answer(Timestampable):
    """All questions from members of parlament."""

    question = models.ForeignKey(
        "Question",
        verbose_name=_("question"),
        help_text=_("The question this answer belongs to."),
        on_delete=models.CASCADE,
        related_name="answers",
    )

    timestamp = models.DateTimeField(
        verbose_name=_("date of the answer."),
        help_text=_("Date of the answer."),
        blank=True,
        null=True,
    )

    text = models.TextField(
        verbose_name=_("text"),
        help_text=_("as written on parlament page."),
        blank=True,
        null=True,
    )

    person_authors = models.ManyToManyField(
        "Person",
        verbose_name=_("authors"),
        help_text=_("The persons (MP) who answered the question."),
        blank=True,
        related_name="authored_ansewrs",
    )

    organization_authors = models.ManyToManyField(
        "Organization",
        verbose_name=_("organization authors"),
        help_text=_("The organizations who answered the question."),
        blank=True,
        related_name="answers_org_author",
    )

    def __str__(self):
        return self.text[:50]
